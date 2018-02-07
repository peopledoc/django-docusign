from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_anysign import api as django_anysign


class SignatureType(django_anysign.SignatureType):
    docusign_template_id = models.CharField(
        _('DocuSign template id'),
        max_length=36,
        blank=True,
    )


class Signature(django_anysign.SignatureFactory(SignatureType)):
    document = models.FileField(
        _('document'),
        upload_to='signatures',
        blank=True,
        null=True,
    )
    document_title = models.CharField(
        _('title'),
        max_length=100,
        blank=True,
        default='',
    )
    status = models.CharField(
        _('status'),
        max_length=50,
        db_index=True,
        choices=(
            ('draft', _('draft')),
            ('sent', _('sent')),
            ('delivered', _('delivered')),
            ('completed', _('completed')),
            ('declined', _('declined')),
        ),
        default='draft',
    )
    status_datetime = models.DateTimeField(
        _('status datetime'),
        auto_now_add=True,
    )

    def signature_documents(self):
        """Return list of documents (file wrappers) to sign.

        Part of `django_anysign`'s API implementation.

        """
        self.document.open()
        self.document.bytes = self.document
        yield self.document


class Signer(django_anysign.SignerFactory(Signature)):
    full_name = models.CharField(
        _('full name'),
        max_length=50,
        db_index=True,
    )
    email = models.EmailField(
        _('email'),
        db_index=True,
    )
    status = models.CharField(
        _('status'),
        max_length=50,
        db_index=True,
        choices=(
            ('draft', _('draft')),
            ('sent', _('sent')),
            ('delivered', _('delivered')),
            ('completed', _('completed')),
            ('declined', _('declined')),
        ),
        default='draft',
    )
    status_datetime = models.DateTimeField(
        _('status datetime'),
        auto_now_add=True,
    )
    status_details = models.CharField(
        _('status details'),
        max_length=250,
        blank=True,
    )
