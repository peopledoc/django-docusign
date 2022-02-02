"""Forms and helpers for DocuSign."""
from __future__ import unicode_literals

from django import forms
from django.utils.translation import gettext_lazy as _


class SignerForm(forms.Form):
    """A form for signer."""
    name = forms.CharField(
        label=_("name"),
        max_length=50,
    )
    email = forms.EmailField(
        label=_("e-mail"),
    )


class PositionedTabForm(forms.Form):
    """A form for a positioned signing tab (place where signer signs)."""
    page_number = forms.IntegerField(
        label=_('page number'),
        min_value=1,
    )
    x_position = forms.IntegerField(
        label=_('x position'),
        min_value=0,
    )
    y_position = forms.IntegerField(
        label=_('y position'),
        min_value=0,
    )


class SignHereTabForm(PositionedTabForm):
    pass


class ApproveTabForm(PositionedTabForm):
    pass
