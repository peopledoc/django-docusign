from django.db import transaction
from django.http import HttpResponse
from django.views.generic.base import ContextMixin, View
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin

import pydocusign
from django_anysign import api as django_anysign


class SignerReturnView(SingleObjectMixin, RedirectView):
    """Handle return of signer on project after document signing/reject.
    """
    permanent = False

    def get_queryset(self):
        model = django_anysign.get_signer_model()
        return model.objects.all()

    @property
    def signature(self):
        """Signature model instance.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_signature`.

        """
        try:
            return self._signature
        except AttributeError:
            self._signature = self.get_object().signature
            return self._signature

    @property
    def signature_backend(self):
        try:
            return self._signature_backend
        except AttributeError:
            self._signature_backend = self.get_signature_backend()
            return self._signature_backend

    def get_signature_backend(self):
        """Return signature backend instance."""
        return self.signature.signature_backend

    def get_signer_with_return_callback_url(self):
        """Url redirect when callbacks are enabled."""
        raise NotImplementedError()

    def get_signer_canceled_url(self, event, status):
        """Url redirect when signer canceled signature."""
        raise NotImplementedError()

    def get_signer_error_url(self, event, status):
        """Url redirect when failure."""
        raise NotImplementedError()

    def get_signer_declined_url(self, event, status):
        """Url redirect when signer declined signature."""
        raise NotImplementedError()

    def get_signer_signed_url(self, event, status):
        """Url redirect when signer signed signature."""
        raise NotImplementedError()

    def get_recipient_status(self, recipient):
        # signature with access code ?
        try:
            auth_status = recipient['recipientAuthenticationStatus']
            access_status = auth_status['accessCodeResult']['status'].lower()
            if 'passed' != access_status:
                return 'authentication_' + access_status
        except KeyError:
            pass
        return recipient['status']

    def get_redirect_url(self, *args, **kwargs):
        """Route request to signer callback depending on status.
        Trigger events for latest signer: calls
        ``signer_{status}`` methods.
        """
        backend = self.signature_backend
        signer = self.get_object()

        # callback compat
        if backend.use_callback:
            return self.get_signer_return_with_callback_url()

        docusign_event = self.request.GET.get('event')
        if docusign_event == 'cancel':
            return self.get_signer_canceled_url(docusign_event, '')

        # get signer infos on docusign side
        recipient = backend.get_docusign_recipient(signer)
        status = self.get_recipient_status(recipient)

        if status == 'authentication_failed':
            self.signer_authenticationfailed()
            return self.get_signer_error_url(docusign_event, status)

        if status == 'auto_responded':
            self.signer_autoresponded()
            return self.get_signer_error_url(docusign_event, status)

        if status == 'completed':
            self.signer_signed()
            return self.get_signer_signed_url(docusign_event, status)

        if status == 'declined':
            decline_message = recipient['declinedReason']
            self.signer_declined(decline_message)
            return self.get_signer_declined_url(docusign_event, status)

        # other status: redirect to canceled page as if action was canceled
        return self.get_signer_canceled_url(docusign_event, status)

    def update_signature(self, status):
        """ Update signature with ``status``."""
        raise NotImplementedError()

    def signature_completed(self):
        """Handle 'completed' status .
        """
        self.update_signature(status='completed')

    def signature_declined(self):
        """Handle 'declined' status ."""
        self.update_signature(status='declined')

    def update_signer(self, status, message=u''):
        """Update ``signer`` with ``status``."""
        raise NotImplementedError()

    def get_signed_document(self):
        # In our model, there is only one doc.
        backend = self.signature_backend
        return next(backend.get_docusign_documents(self.signature))

    def replace_document(self, signed_document):
        """Replace original document by signed one."""
        raise NotImplementedError()

    def signer_declined(self, message):
        """Handle 'Declined' status for signer."""
        self.update_signer(status='declined', message=message)
        self.signature_declined()

    def signer_signed(self):
        """Handle 'Completed' status for signer.
        """
        backend = self.signature_backend
        is_last_signer = backend.is_last_signer(self.get_object())
        # download signed document out of the atomic block
        signed_document = self.get_signed_document()
        with transaction.atomic():
            self.replace_document(signed_document)
            self.update_signer(status='completed')
            if is_last_signer:
                self.signature_completed()

    def signer_authenticationfailed(self):
        """Handle 'AuthenticationFailed' status for signer."""
        self.update_signer(status='authentication_failed')

    def signer_autoresponded(self):
        """Handle 'AutoResponded' status for signer."""
        self.update_signer(status='auto_responded')


class SignatureCallbackView(ContextMixin, View):
    """Handle DocuSign's event notification.

    This view can handle both recipient and envelope events.

    """
    @property
    def docusign_parser(self):
        """Parser for DocuSign's request.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_docusign_parser`.

        """
        try:
            return self._docusign_parser
        except AttributeError:
            self._docusign_parser = self.get_docusign_parser()
            return self._docusign_parser

    def get_docusign_parser(self):
        """Extract, validate and return data from DocuSign's request."""
        parser = pydocusign.DocuSignCallbackParser(
            xml_source=self.request.body)
        return parser

    @property
    def envelope_status(self):
        """Envelope status, extracted from DocuSign input data."""
        return self.docusign_parser.envelope_status

    def post(self, request, *args, **kwargs):
        """Route request to signature callback depending on status.

        Trigger events for latest signer and signature events: calls
        ``signature_{status}`` and ``signer_{status}`` methods.

        """
        signature_event = self.docusign_parser.envelope_events[-1]
        signer_events = []
        if signature_event['status'] == pydocusign.Envelope.STATUS_SENT:
            # If signature status is "sent" and all signers are "sent", then
            # trigger "sent" event for signature and all signers.
            if all([signer_event['status'] == pydocusign.Recipient.STATUS_SENT
                    for signer_event
                    in self.docusign_parser.recipient_events]):
                signer_events = self.docusign_parser.recipient_events
            # Else, do not care about "sent" event for signature.
            else:
                signature_event = None
                signer_events = [self.docusign_parser.recipient_events[-1]]
        else:
            signer_events = [self.docusign_parser.recipient_events[-1]]
        # Trigger signature event.
        if signature_event:
            callback = getattr(self,
                               'signature_{status}'.format(
                                   status=signature_event['status'].lower()))
            callback()
        # Trigger signer events.
        for signer_event in signer_events:
            callback = getattr(self,
                               'signer_{status}'.format(
                                   status=signer_event['status'].lower()))
            callback(signer_id=signer_event['recipient'])
        return HttpResponse()

    @property
    def signature(self):
        """Signature model instance.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_signature`.

        """
        try:
            return self._signature
        except AttributeError:
            self._signature = self.get_signature()
            return self._signature

    def get_signature(self):
        Signature = django_anysign.get_signature_model()
        envelope_id = self.docusign_parser.envelope_id
        return Signature.objects.get(signature_backend_id=envelope_id)

    @property
    def signature_backend(self):
        """Signature backend instance.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_signature_backend`.

        """
        try:
            return self._signature_backend
        except AttributeError:
            self._signature_backend = self.get_signature_backend()
            return self._signature_backend

    def get_signature_backend(self):
        """Return signature backend instance.

        Default implementation calls signature instance's
        ``signature_backend``. Override this method if you want a custom
        backend initialization.

        """
        return self.signature.signature_backend

    def update_signer(self, signer_id, status, status_datetime=None,
                      message=u''):
        """Update ``signer`` with ``status``.

        Additional ``status_datetime`` argument is the datetime mentioned by
        DocuSign.

        """
        raise NotImplementedError()

    def update_signature(self, status, status_datetime=None):
        """ Update signature with ``datetime``.

        Additional ``status_datetime`` argument is the datetime mentioned by
        DocuSign.

        """
        raise NotImplementedError()

    def signature_sent(self):
        """Handle 'sent' status reported by DocuSign callback.

        Default implementation just calls :meth:`update_signer` with status.

        """
        self.update_signature(
            status='sent',
            status_datetime=self.docusign_parser.envelope_status_datetime(
                'Sent'))

    def signature_delivered(self):
        """Handle 'delivered' status reported by DocuSign callback.

        Default implementation just calls :meth:`update_signer` with status.

        """
        self.update_signature(
            status='delivered',
            status_datetime=self.docusign_parser.envelope_status_datetime(
                'Delivered'))

    def signature_completed(self):
        """Handle 'completed' status reported by DocuSign callback.

        Default implementation calls :meth:`update_signer` and
        :meth:`update_signature` with status.

        """
        self.update_signature(
            status='completed',
            status_datetime=self.docusign_parser.envelope_status_datetime(
                'Completed'))

    def signature_declined(self):
        """Handle 'declined' status reported by DocuSign callback."""
        self.update_signature(
            status='declined',
            status_datetime=self.docusign_parser.envelope_status_datetime(
                'Declined'))

    def signer_sent(self, signer_id):
        """Handle 'Sent' status reported by DocuSign for signer."""
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='sent',
            status_datetime=recipient['Sent'],
        )

    def signer_delivered(self, signer_id):
        """Handle 'Delivered' status reported by DocuSign for signer."""
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='delivered',
            status_datetime=recipient['Delivered'],
        )

    def signer_signed(self, signer_id):
        """Handle 'Signed' event reported by DocuSign for signer.

        Notice that recipient status is 'Completed' whereas event is 'Signed'.

        """
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='completed',
            status_datetime=recipient['Completed'],
        )

    def signer_declined(self, signer_id):
        """Handle 'Declined' status reported by DocuSign for signer."""
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='declined',
            status_datetime=recipient['Declined'],
            message=recipient.get('DeclineReason', u''),
        )

    def signer_authenticationfailed(self, signer_id):
        """Handle 'AuthenticationFailed' status for signer."""
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='authentication_failed',
            status_datetime=recipient['AuthenticationFailed'],
        )

    def signer_autoresponded(self, signer_id):
        """Handle 'AutoResponded' status reported by DocuSign for signer."""
        recipient = self.docusign_parser.recipients[signer_id]
        self.update_signer(
            signer_id,
            status='auto_responded',
            status_datetime=recipient['AutoResponded'],
        )
