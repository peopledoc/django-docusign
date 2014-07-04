import django_anysign
import pydocusign


class DocuSignBackend(django_anysign.SignatureBackend):
    def __init__(self, name, code, url_namespace='anysign', **kwargs):
        """Setup.

        Additional keyword arguments are passed to
        :class:`~pydocusign.backend.DocuSignBackend` constructor, in order to
        setup :attr:`docusign_client`.

        """
        super(DocuSignBackend, self).__init__(
            name='DocuSign',
            code='docusign',
            url_namespace=url_namespace,
        )
        #: Instance of :class:`~pydocusign.client.DocuSignClient`
        self.docusign_client = pydocusign.DocuSignClient(**kwargs)

    def create_signature(self, signature):
        """Register ``signature`` in DocuSign service, return updated object.

        This method calls ``save()`` on ``signature``.

        """
        # Prepare signers.
        signers = [
            pydocusign.Signer(
                email=signer.email,
                name=signer.full_name,
                recipientId=signer.pk,
                clientUserId=signer.pk,
                tabs=[
                    pydocusign.SignHereTab(
                        documentId=1,
                        pageNumber=1,
                        xPosition=100,
                        yPosition=100,
                    ),
                ],
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

    def post_recipient_view(self, signer):
        # Prepare signers.
        signers = [
            pydocusign.Signer(
                email=every_signer.email,
                name=every_signer.full_name,
                recipientId=every_signer.pk,
                clientUserId=every_signer.pk,
                tabs=[
                    pydocusign.SignHereTab(
                        documentId=1,
                        pageNumber=1,
                        xPosition=100,
                        yPosition=100,
                    ),
                ],
            ) for every_signer in signer.signature.signers.all()
        ]
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            envelopeId=signer.signature.signature_backend_id,
            recipients=signers,
        )
        envelope.get_recipients(client=self.docusign_client)
        return envelope.post_recipient_view(
            client=self.docusign_client,
            routingOrder=signer.signing_order,
            returnUrl=self.get_signer_return_url(signer)
        )
