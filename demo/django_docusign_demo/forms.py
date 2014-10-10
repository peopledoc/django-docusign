"""Demo forms for `django-docusign`."""
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from django_docusign import SignerForm
from formsetfield.fields import FormSetField


class SettingsForm(forms.Form):
    """DocuSign API credentials."""
    root_url = forms.URLField(
        label=_('API root URL'),
        initial=_('https://demo.docusign.net/restapi/v2'),
    )
    username = forms.CharField(
        label=_('username'),
        max_length=50,
    )
    password = forms.CharField(
        label=_('password'),
        max_length=50,
    )
    integrator_key = forms.CharField(
        label=_('integrator key'),
        max_length=50,
    )
    signer_return_url = forms.URLField(
        label=_('signer return URL'),
    )
    callback_url = forms.URLField(
        label=_('callback URL'),
    )


class CreateSignatureForm(forms.Form):
    """Signature creation form."""
    document = forms.FileField(
        label=_('document'),
    )
    title = forms.CharField(
        label=_('title'),
        max_length=100,
        help_text=_("Title for the document."),
    )
    signers = FormSetField(
        formset_factory(SignerForm, extra=2),
        label=_('signers'),
    )
    callback_url = forms.URLField(
        label=_('API callback URL'),
    )
