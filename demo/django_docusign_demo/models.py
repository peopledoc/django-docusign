import django_anysign


class SignatureType(django_anysign.SignatureType):
    pass


class Signature(django_anysign.SignatureFactory(SignatureType)):
    pass


class Signer(django_anysign.SignerFactory(Signature)):
    pass
