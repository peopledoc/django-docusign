from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

from bs4 import BeautifulSoup
import django_anysign


class SignatureCallbackView(TemplateResponseMixin, ContextMixin, View):
    """Handle DocuSign's event notification."""
    template_name = 'docusign/signature_callback.html'

    @property
    def docusign_data(self):
        """Data dictionary from DocuSign's request.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_docusign_data`.

        """
        try:
            return self._docusign_data
        except AttributeError:
            self._docusign_data = self.get_docusign_data()
            return self._docusign_data

    def get_docusign_data(self):
        """Extract, validate and return data from DocuSign's request."""
        data = BeautifulSoup(self.request.body, ["lxml", "xml"])
        self.clean_status(data.EnvelopeStatus
                              .RecipientStatuses
                              .RecipientStatus
                              .Status
                              .string)
        return data

    def clean_status(self, value):
        """Validate and return normalized value of ``status``."""
        status = value.lower()
        if status is None:
            raise Exception('Could not parse callback request body.')
        allowed_status_list = ['sent', 'delivered', 'completed', 'declined']
        if status not in allowed_status_list:
            raise Exception('Unknown status {status}'.format(status=status))
        return status

    @property
    def envelope_status(self):
        """Envelope status, extracted from DocuSign input data."""
        return self.docusign_data.EnvelopeStatus \
                                 .RecipientStatuses \
                                 .RecipientStatus \
                                 .Status \
                                 .string \
                                 .lower()

    def post(self, request, *args, **kwargs):
        """Route request to signature callback depending on status.

        Calls ``signature_{status}`` method.

        """
        callback = getattr(self,
                           'signature_{status}'.format(
                               status=self.envelope_status))
        callback()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Return context data.

        Updates default data with ``signature`` and ``signer``.

        """
        data = super(SignatureCallbackView, self).get_context_data(**kwargs)
        data['signature'] = self.signature
        data['signer'] = self.signer
        return data

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
        envelope_id = self.docusign_data.EnvelopeStatus.EnvelopeID.string
        return Signature.objects.get(signature_backend_id=envelope_id)

    @property
    def signer(self):
        """Signer model instance.

        This is a shortcut property using a cache.
        If you want to adapt the implementation, consider overriding
        :meth:`get_signer`.

        """
        try:
            return self._signer
        except AttributeError:
            self._signer = self.get_signer()
            return self._signer

    def get_signer(self):
        signer_id = self.docusign_data \
                        .EnvelopeStatus \
                        .RecipientStatuses \
                        .RecipientStatus \
                        .ClientUserId \
                        .string
        return self.signature.signers.get(pk=signer_id)

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

    def update_signer(self, status):
        raise NotImplementedError()

    def update_signature(self, status):
        raise NotImplementedError()

    def signature_sent(self):
        """Handle 'sent' status reported by DocuSign callback.

        Default implementation just calls :meth:`update_signer` with status.

        """
        self.update_signer(status='sent')

    def signature_delivered(self):
        """Handle 'delivered' status reported by DocuSign callback.

        Default implementation just calls :meth:`update_signer` with status.

        """
        self.update_signer(status='delivered')

    def signature_completed(self):
        """Handle 'completed' status reported by DocuSign callback.

        Default implementation calls :meth:`update_signer` and
        :meth:`update_signature` with status.

        """
        self.update_signature(status='completed')
        self.update_signer(status='completed')

    def signature_declined(self):
        """Handle 'declined' status reported by DocuSign callback.

        Default implementation calls :meth:`update_signer` with status and
        optional signer's message.

        """
        self.update_signer(status='declined',
                           message=self.docusign_data
                                       .EnvelopeStatus
                                       .RecipientStatuses
                                       .RecipientStatus
                                       .DeclineReason
                                       .string)
