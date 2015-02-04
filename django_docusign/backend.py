from django.conf import settings

import django_anysign
import pydocusign


class DocuSignBackend(django_anysign.SignatureBackend):
    def __init__(self, name='DocuSign', code='docusign',
                 url_namespace='anysign', **kwargs):
        """Setup.

        Additional ``kwargs`` are proxied to
        :class:`pydocusign.DocuSignClient`.

        """
        super(DocuSignBackend, self).__init__(
            name=name,
            code=code,
            url_namespace=url_namespace,
        )
        client_kwargs = self.get_client_kwargs(**kwargs)
        #: Instance of :class:`~pydocusign.client.DocuSignClient`
        self.docusign_client = pydocusign.DocuSignClient(**client_kwargs)

    def get_client_kwargs(self, **kwargs):
        """Return keyword arguments for use with DocuSign client factory.

        Uses, in order (the latter override the former):

        1. ``settings.DOCUSIGN_*``
        2. ``kwargs``

        .. note::

           :class:`pydocusign.DocuSignClient` itself uses environment
           variables ``DOCUSIGN_*`` if available.

        """
        client_kwargs = {}
        for key in ['root_url',
                    'username',
                    'password',
                    'integrator_key',
                    'account_id',
                    'account_url',
                    'app_token',
                    'timeout']:
            setting_name = 'DOCUSIGN_{0}'.format(key.upper())
            try:
                client_kwargs[key] = getattr(settings, setting_name)
            except AttributeError:
                pass
        client_kwargs.update(kwargs)
        return client_kwargs

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
        for signer in signature.signers.all().order_by('signing_order'):
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

    def get_docusign_roles(self, signature):
        """Return list of pydocusign's Role for Signature instance.

        Default implementation reads name, email and role name from database.

        """
        # Get docusign template definition, to retrieve role names
        template_definition = self.docusign_client.get_template(
            signature.signature_type.docusign_template_id)
        template_roles = template_definition['recipients']['signers']
        roles = []
        # Build roles
        for signer in signature.signers.all().order_by('signing_order'):
            role = pydocusign.Role(
                email=signer.email,
                name=signer.full_name,
                roleName=template_roles[signer.signing_order - 1]['roleName'],
                clientUserId=signer.pk,
            )
            roles.append(role)
        return roles

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

    def create_signature_from_document(self, signature, callback_url=None,
                                       subject=u'', blurb=u''):
        """Register ``signature`` in DocuSign service, for a signature from
        document.

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
            emailSubject=subject,
            emailBlurb=blurb,
            eventNotification=event_notification,
            status=pydocusign.Envelope.STATUS_SENT,
            documents=documents,
            recipients=signers,
        )
        envelope.envelopeId = self.docusign_client \
                                  .create_envelope_from_document(envelope)
        return envelope

    def create_signature_from_template(self, signature, callback_url=None,
                                       subject=u'', blurb=u''):
        """Register ``signature`` in DocuSign service, for a signature from
        document.

        """
        # Prepare roles.
        roles = self.get_docusign_roles(signature)
        # Prepare event notifications (callbacks).
        if callback_url is None:
            callback_url = self.get_signature_callback_url(signature)
        event_notification = pydocusign.EventNotification(
            url=callback_url,
        )
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            emailSubject=subject,
            emailBlurb=blurb,
            eventNotification=event_notification,
            status=pydocusign.Envelope.STATUS_SENT,
            templateId=signature.signature_type.docusign_template_id,
            templateRoles=roles,
        )
        envelope.envelopeId = self.docusign_client \
                                  .create_envelope_from_template(envelope)
        return envelope

    def create_signature(self, signature, callback_url=None,
                         subject=u'', blurb=u''):
        """Register ``signature`` in DocuSign service, return updated object.

        This method calls ``save()`` on ``signature``.

        """
        if signature.signature_type.docusign_template_id:
            envelope = self.create_signature_from_template(
                signature, callback_url, subject, blurb)
        else:
            envelope = self.create_signature_from_document(
                signature, callback_url, subject, blurb)
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
            ) for every_signer in signer.signature
                                        .signers
                                        .all()
                                        .order_by('signing_order')
        ]
        # Create envelope with embedded signing.
        envelope = pydocusign.Envelope(
            envelopeId=signer.signature.signature_backend_id,
            recipients=signers,
        )
        if position is None:
            position = signer.signing_order
        if signer_return_url is None:
            signer_return_url = self.get_signer_return_url(signer)
        envelope.get_recipients(client=self.docusign_client)
        return envelope.post_recipient_view(
            client=self.docusign_client,
            routingOrder=position,
            returnUrl=signer_return_url
        )
