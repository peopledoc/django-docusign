from django.db import models
from django.utils.translation import ugettext_lazy as _

import django_anysign


class SignatureType(django_anysign.SignatureType):
    pass


class Signature(django_anysign.SignatureFactory(SignatureType)):
    document = models.FileField(
        _('document'),
        upload_to='signatures',
        blank=True,
        null=True,
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
