"""Demo forms for `django-docusign`."""
from django import forms
from django.utils.translation import ugettext_lazy as _


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
    signer_name = forms.CharField(
        label=_("Signer's name"),
        max_length=50,
    )
    signer_email = forms.EmailField(
        label=_("Signer's email"),
    )
