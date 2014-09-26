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

    def get_docusign_tabs(self, signer):
        """Return list of pydocusign's tabs for Signer instance.

        Default implementation returns no tab, i.e. the signer chooses where to
        sign!

        """
        return []

    def get_docusign_signers(self, signature):
        """Return list of pydocusign's Signer for Signature instance.

        Default implementation reads name and email from database.

        """
        signers = []
        for signer in signature.signers.all():
            tabs = self.get_docusign_tabs(signer)
            signer = pydocusign.Signer(
                email=signer.email,
                name=signer.full_name,
                recipientId=signer.pk,
                clientUserId=signer.pk,
                tabs=tabs,
            )
            signers.append(signer)
        return signers

    def get_docusign_documents(self, signature):
        """Generate list of documents for ``signature`` model instance.

        Ignores special document "certificate".

        Yields file-like objects.

        .. warning:: Close returned documents!

        """
        envelope_id = signature.signature_backend_id
        document_list = self.docusign_client \
                            .get_envelope_document_list(envelope_id)
        for document_data in document_list:
            document_id = document_data['documentId']
            if document_id != 'certificate':
                document = self.docusign_client \
                               .get_envelope_document(envelope_id, document_id)
                yield document

    def create_signature(self, signature, callback_url=None):
        """Register ``signature`` in DocuSign service, return updated object.

        This method calls ``save()`` on ``signature``.

        """
        # Prepare signers.
        signers = self.get_docusign_signers(signature)
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
        # Prepare event notifications (callbacks).
        if callback_url is None:
            callback_url = self.get_signature_callback_url(signature)
        event_notification = pydocusign.EventNotification(
            url=callback_url,
        )
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            emailSubject='This is the subject',
            emailBlurb='This is the body',
            eventNotification=event_notification,
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
