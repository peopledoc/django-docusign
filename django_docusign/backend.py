import django_anysign
import pydocusign


class DocuSignBackend(django_anysign.SignatureBackend):
    def __init__(self, name='DocuSign', code='docusign',
                 url_namespace='anysign', **kwargs):
        """Setup.

        Additional keyword arguments are passed to
        :class:`~pydocusign.backend.DocuSignBackend` constructor, in order to
        setup :attr:`docusign_client`.

        """
        super(DocuSignBackend, self).__init__(
            name=name,
            code=code,
            url_namespace=url_namespace,
        )
        #: Instance of :class:`~pydocusign.client.DocuSignClient`
        self.docusign_client = pydocusign.DocuSignClient(**kwargs)

    def create_signature(self, signature, tabs=None):
        """Register ``signature`` in DocuSign service, return updated object.

        This method calls ``save()`` on ``signature``.
        """
        tabs = tabs or []
        pydocusign_tabs = {}
        for tab in tabs:
            tab_class = None
            if tab['type'] in ['SignHereTab', 'ApproveTab']:
                tab_class = getattr(pydocusign, tab['type'])

            if tab_class is not None:
                pydocusign_tabs.setdefault(tab['signer'], [])
                pydocusign_tabs[tab['signer']].append(tab_class(**tab['attributes']))

        # Prepare signers.
        signers = [
            pydocusign.Signer(
                email=signer.email,
                name=signer.full_name,
                recipientId=signer.pk,
                clientUserId=signer.pk,
                tabs=pydocusign_tabs.get(signer.pk),
            ) for signer in signature.signers.all()
        ]
        # Prepare documents.
        documents = []
        i = 1
        for document in signature.signature_documents():
            documents.append(
                pydocusign.Document(
                    name=document.name,
                    documentId=i,
                    data=document.bytes,
                )
            )
            i += 1
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            emailSubject='This is the subject',
            emailBlurb='This is the body',
            status=pydocusign.Envelope.STATUS_SENT,
            documents=documents,
            recipients=signers,
        )
        envelope.envelopeId = self.docusign_client \
                                  .create_envelope_from_document(envelope)
        # Update signature instance with backend's ID.
        signature.signature_backend_id = envelope.envelopeId
        signature.save()
        # Return updated object.
        return signature

    def post_recipient_view(self, signer, position=None,
                            signer_return_url=None):
        # Prepare signers.
        signers = [
            pydocusign.Signer(
                email=every_signer.email,
                name=every_signer.full_name,
                recipientId=every_signer.pk,
                clientUserId=every_signer.pk,
            ) for every_signer in signer.signature.signers.all()
        ]
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            envelopeId=signer.signature.signature_backend_id,
            recipients=signers,
        )
        if position is None:
            position = list(signer.signature.signers.all()).index(signer)
        if signer_return_url is None:
            self.get_signer_return_url(signer)
        envelope.get_recipients(client=self.docusign_client)
        return envelope.post_recipient_view(
            client=self.docusign_client,
            routingOrder=position,
            returnUrl=signer_return_url
        )
