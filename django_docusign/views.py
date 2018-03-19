from __future__ import unicode_literals

from django.db import transaction
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin
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
        """Route request to signer return view depending on status.
        Trigger events for latest signer: calls
        ``signer_{status}`` methods.
        """
        backend = self.signature_backend
        signer = self.get_object()

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

    def update_signer(self, status, message=''):
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
