"""Demo views for `django-docusign`."""
import os

import django_anysign

from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from django_docusign_demo import forms
from django_docusign_demo import models


def docusign_setting(request, name):
    """Return setting by ``name`` from request.session or environ."""
    return request.session.get(name, os.environ.get(name))


def docusign_settings(request):
    """Return dictionary of credentials for DocuSign, from session or environ.

    Values are read from session, and fallback to environ.

    """
    return {
        'root_url': docusign_setting(request, 'PYDOCUSIGN_TEST_ROOT_URL'),
        'username': docusign_setting(request, 'PYDOCUSIGN_TEST_USERNAME'),
        'password': docusign_setting(request, 'PYDOCUSIGN_TEST_PASSWORD'),
        'integrator_key': docusign_setting(
            request, 'PYDOCUSIGN_TEST_INTEGRATOR_KEY'),
    }


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
            self.request.session[key] = value
        return super(SettingsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home')

    def get_initial(self):
        return docusign_settings(self.request)


class CreateSignatureView(FormView):
    """Create DocuSign envelope."""
    form_class = forms.CreateSignatureForm
    template_name = 'create_signature.html'

    def get_success_url(self):
        """Return home URL."""
        return reverse('home')

    def form_valid(self, form):
        """Create envelope on DocuSign's side."""
        # Prepare signature instance with uploaded document, Django side.
        (signature_type, created) = models.SignatureType.objects.get_or_create(
            signature_backend_code='docusign')
        signature = models.Signature.objects.create(
            signature_type=signature_type,
            document=self.request.FILES['document'],
        )
        # Add signers (only one in this implementation).
        signature.signers.create(
            full_name=form.cleaned_data['signer_name'],
            email=form.cleaned_data['signer_email'],
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
        self.signature_backend.create_signature(signature)


class SignerView(SingleObjectMixin, RedirectView):
    """Embed DocuSign's recipient view."""
    model = models.Signer

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


class SignerReturnView(TemplateView):
    """Welcome the signer back from DocuSign."""
    template_name = 'signer_return.html'
