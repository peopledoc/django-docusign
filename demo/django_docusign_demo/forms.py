"""Demo forms for `django-docusign`."""
from __future__ import unicode_literals

from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import gettext_lazy as _
from django_docusign import api as django_docusign

from .formsetfield.fields import FormSetField


class SettingsForm(forms.Form):
    """DocuSign API credentials."""
    root_url = forms.URLField(
        label=_('API root URL'),
        required=False,
        initial=_('https://demo.docusign.net/restapi/v2'),
    )
    username = forms.CharField(
        label=_('username'),
        required=False,
        max_length=50,
    )
    password = forms.CharField(
        label=_('password'),
        required=False,
        max_length=50,
    )
    integrator_key = forms.CharField(
        label=_('integrator key'),
        required=False,
        max_length=50,
    )
    timeout = forms.FloatField(
        label=_('timeout'),
        required=False,
        min_value=0.001,
        max_value=30,
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
        formset_factory(django_docusign.SignerForm, extra=2),
        label=_('signers'),
    )


class CreateSignatureTemplateForm(forms.Form):
    """Signature from template creation form."""
    template_id = forms.CharField(
        label=_('template id'),
        max_length=36,
    )
    title = forms.CharField(
        label=_('title'),
        max_length=100,
        help_text=_("Title for the document."),
    )
    signers = FormSetField(
        formset_factory(django_docusign.SignerForm, extra=2),
        label=_('signers'),
    )
