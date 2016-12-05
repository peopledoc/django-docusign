"""Demo views for `django-docusign`."""
import os

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.utils.text import slugify
from django.utils.timezone import now

from django_anysign import api as django_anysign
from django_docusign import api as django_docusign

from django_docusign_demo import forms
from django_docusign_demo import models


def docusign_settings(request):
    """Return dictionary of credentials for DocuSign from session or environ.

    Values are read from session, and fallback to environ.

    """
    data = {}
    for key in ['root_url', 'username', 'password', 'integrator_key',
                'timeout', 'use_callback']:
        try:
            data[key] = request.session[key]
        except KeyError:
            pass
    return data


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        data = super(HomeView, self).get_context_data(**kwargs)
        data['has_settings'] = all(docusign_settings(self.request))
        data['latest_signatures'] = models.Signature.objects \
            .all() \
            .order_by('-pk')[0:5]
        return data


class SettingsView(FormView):
    """Store DocuSign settings in session."""
    form_class = forms.SettingsForm
    template_name = 'settings.html'

    def form_valid(self, form):
        """Save configuration in session."""
        data = form.cleaned_data
        for (key, value) in data.items():
            if value or isinstance(value, bool):
                self.request.session[key] = value
        return super(SettingsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home')

    def get_initial(self):
        return docusign_settings(self.request)

    def get_context_data(self, **kwargs):
        data = super(SettingsView, self).get_context_data(**kwargs)
        data['default_backend'] = django_docusign.DocuSignBackend()
        return data


class CreateSignatureView(FormView):
    """Create DocuSign envelope."""
    form_class = forms.CreateSignatureForm
    template_name = 'create_signature.html'

    def get_success_url(self):
        """Return home URL."""
        return reverse('home')

    def get_form_kwargs(self):
        kwargs = super(CreateSignatureView, self).get_form_kwargs()
        kwargs.update({
            'use_callback': self.signature_backend.use_callback
        })
        return kwargs

    def form_valid(self, form):
        """Create envelope on DocuSign's side."""
        self.cleaned_data = form.cleaned_data
        # Prepare signature instance with uploaded document, Django side.
        (signature_type, created) = models.SignatureType.objects.get_or_create(
            signature_backend_code='docusign',
            docusign_template_id='')
        signature = models.Signature.objects.create(
            signature_type=signature_type,
            document=self.request.FILES['document'],
            document_title=self.cleaned_data['title'],
        )
        # Add signers.
        for position, signer_data in enumerate(self.cleaned_data['signers']):
            signature.signers.create(
                full_name=signer_data['name'],
                email=signer_data['email'],
                signing_order=position + 1,  # Position starts at 1.
            )
        # Create signature, backend side.
        self.create_signature(signature)
        return super(CreateSignatureView, self).form_valid(form)

    @property
    def signature_backend(self):
        try:
            return self._signature_backend
        except AttributeError:
            self._signature_backend = self.get_signature_backend()
            return self._signature_backend

    def get_signature_backend(self):
        """Return signature backend instance."""
        backend_settings = docusign_settings(self.request)
        signature_backend = django_anysign.get_signature_backend(
            'docusign',
            **backend_settings
        )
        return signature_backend

    def create_signature(self, signature):
        """Create signature backend-side."""
        params = {}
        if self.signature_backend.use_callback:
            params['callback_url'] = self.cleaned_data['callback_url']
        self.signature_backend.create_signature(
            signature,
            subject=signature.document_title,
            **params
        )


class CreateSignatureTemplateView(CreateSignatureView):
    """Create DocuSign envelope."""
    form_class = forms.CreateSignatureTemplateForm
    template_name = 'create_signature_template.html'

    def get_initial(self):
        """template_id initial value."""
        initial = self.initial.copy()
        initial['template_id'] = os.environ.get('DOCUSIGN_TEST_TEMPLATE_ID')
        return initial

    def form_valid(self, form):
        """Create envelope on DocuSign's side."""
        self.cleaned_data = form.cleaned_data
        # Prepare signature instance with uploaded document, Django side.
        (signature_type, created) = models.SignatureType.objects.get_or_create(
            signature_backend_code='docusign',
            docusign_template_id=self.cleaned_data['template_id'])
        signature = models.Signature.objects.create(
            signature_type=signature_type,
            document_title=self.cleaned_data['title'],
        )
        # Add signers.
        for position, signer_data in enumerate(self.cleaned_data['signers']):
            signature.signers.create(
                full_name=signer_data['name'],
                email=signer_data['email'],
                signing_order=position + 1,  # Position starts at 1.
            )
        # Create signature, backend side.
        self.create_signature(signature)
        return super(CreateSignatureView, self).form_valid(form)


class SignerView(SingleObjectMixin, RedirectView):
    """Embed DocuSign's recipient view."""
    model = models.Signer
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Return URL where signer is redirected once doc has been signed."""
        signer = self.get_object()
        backend_settings = docusign_settings(self.request)
        signature_backend = django_anysign.get_signature_backend(
            'docusign',
            **backend_settings
        )
        signer_return_url = self.request.build_absolute_uri(
            signature_backend.get_signer_return_url(signer))
        url = signature_backend.post_recipient_view(
            signer, signer_return_url=signer_return_url)
        return url


class SignerReturnView(django_docusign.SignerReturnView):
    """Welcome the signer back from DocuSign."""

    def get_signature_backend(self):
        """Return signature backend instance."""
        backend_settings = docusign_settings(self.request)
        signature_backend = django_anysign.get_signature_backend(
            'docusign',
            **backend_settings
        )
        return signature_backend

    def get_signer_return_with_callback_url(self):
        """Url redirect when callbacks are enabled."""
        return reverse('anysign:signer_return_with_callback',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def get_signer_canceled_url(self, event, status):
        """Url redirect when signer canceled signature."""
        return reverse('anysign:signer_canceled',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def get_signer_error_url(self, event, status):
        """Url redirect when failure."""
        return reverse('anysign:signer_error',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def get_signer_declined_url(self, event, status):
        """Url redirect when signer declined signature."""
        return reverse('anysign:signer_declined',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def get_signer_signed_url(self, event, status):
        """Url redirect when signer signed signature."""
        return reverse('anysign:signer_signed',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def update_signer(self, status, message=u''):
        """Update ``signer`` with ``status``.
        Additional ``status_datetime`` argument is the datetime mentioned by
        DocuSign.
        """
        signer = self.get_object()
        signer.status = status
        signer.status_datetime = now()
        signer.status_details = message
        signer.save()

    def update_signature(self, status):
        self.signature.status = status
        self.signature.save()

    def replace_document(self, signed_document):
        # Replace old document by signed one.
        filename = self.signature.document.name
        if not filename:
            filename = "%s.pdf" % slugify(
                self.signature.document_title)
        self.signature.document.delete(save=False)
        self.signature.document.save(filename,
                                     ContentFile(signed_document.read()),
                                     save=True)


class SignerReturnWithCallbackView(TemplateView):
    template_name = 'signer_return.html'


class SignerCanceledView(TemplateView):
    template_name = 'signer_canceled.html'


class SignerErrorView(TemplateView):
    template_name = 'signer_error.html'


class SignerDeclinedView(TemplateView):
    template_name = 'signer_declined.html'


class SignerSignedView(TemplateView):
    template_name = 'signer_signed.html'


class SignatureCallbackView(django_docusign.SignatureCallbackView):
    def get_signature_backend(self):
        """Return signature backend instance."""
        backend_settings = docusign_settings(self.request)
        signature_backend = django_anysign.get_signature_backend(
            'docusign',
            **backend_settings
        )
        return signature_backend

    def update_signer(self, signer_id, status, status_datetime=None,
                      message=u''):
        signer = django_anysign.get_signer_model().objects.get(pk=signer_id)
        signer.status = status
        signer.status_datetime = status_datetime or now()
        signer.status_details = message
        signer.save()

    def update_signature(self, status, status_datetime=None):
        self.signature.status = status
        self.signature.save()
        if status == 'completed' or not self.signature.document:
            document = next(self.signature_backend.get_docusign_documents(
                self.signature))  # In our model, there is only one doc.
            # Replace old document by signed one.
            filename = self.signature.document.name
            if not filename:
                filename = "%s.pdf" % slugify(
                    self.signature.document_title)
            self.signature.document.delete(save=False)
            self.signature.document.save(filename,
                                         ContentFile(document.read()),
                                         save=True)
