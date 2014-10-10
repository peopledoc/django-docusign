# coding=utf8
import os

from django.core.urlresolvers import reverse
import django.test

from django_docusign_demo import models


here = os.path.abspath(os.path.dirname(__file__))
fixtures_dir = os.path.join(here, 'fixtures')


class SignatureFunctionalTestCase(django.test.TestCase):
    """Functional test suite for 'create_signature' URL."""
    #: Class-level signature instance, in order to reduce API calls.
    _signature = None

    @property
    def signature(self):
        """Get or create signature instance."""
        if self._signature is None:
            self.assertEqual(models.Signature.objects.all().count(), 0)
            url = reverse('create_signature')
            with open(os.path.join(fixtures_dir, 'test.pdf')) as document_file:
                data = {
                    'signers-TOTAL_FORMS': u'2',
                    'signers-INITIAL_FORMS': u'0',
                    'signers-MAX_NUM_FORMS': u'1000',
                    'signers-0-name': u'John Accentué',
                    'signers-0-email': u'john@example.com',
                    'signers-1-name': u'Paul Doe',
                    'signers-1-email': u'paul@example.com',
                    'document': document_file,
                    'title': u'A very simple PDF document',
                    'callback_url': u'http://tech.novapost.fr',
                }
                response = self.client.post(url, data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('home'))
            self.assertEqual(models.Signature.objects.all().count(), 1)
            self._signature = models.Signature.objects.get()
        return self._signature

    def test_form_valid(self):
        """Can create a signature using 'create_signature' URL."""
        self.assertTrue(self.signature.signature_backend_id)

    def test_signer_view(self):
        """Signer view redirects to DocuSign."""
        url = reverse('anysign:signer',
                      args=[self.signature.signers.all()[0].pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertTrue(
            response['Location'].startswith('https://demo.docusign.net'))

    def _test_signature_callback(self, status, envelope_id, signer_id):
        signer = self.signature.signers.first()
        self.assertEqual(signer.status, 'draft')
        url = reverse('anysign:signature_callback')
        request_body = open(
            os.path.join(fixtures_dir,
                         'callback_{status}.xml'.format(status=status))).read()
        request_body = request_body.replace(
            '<EnvelopeID>{uuid}</EnvelopeID>'.format(uuid=envelope_id),
            '<EnvelopeID>{uuid}</EnvelopeID>'.format(
                uuid=self.signature.signature_backend_id))
        request_body = request_body.replace(
            '<ClientUserId>{id}</ClientUserId>'.format(id=signer_id),
            '<ClientUserId>{id}</ClientUserId>'.format(
                id=signer.pk))
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)
        signer = self.signature.signers.first()
        self.assertEqual(signer.status, status)

    def test_signature_sent_callback(self):
        """Callback view handles DocuSign's 'sent' status."""
        self._test_signature_callback(
            'sent',
            '62d077fc-e912-4854-acac-da30a7c9854b',
            '6',
        )

    def test_signature_delivered_callback(self):
        """Callback view handles DocuSign's 'delivered' status."""
        self._test_signature_callback(
            'delivered',
            '62d077fc-e912-4854-acac-da30a7c9854b',
            '6',
        )

    def test_signature_completed_callback(self):
        """Callback view handles DocuSign's 'completed' status."""
        self._test_signature_callback(
            'completed',
            '62d077fc-e912-4854-acac-da30a7c9854b',
            '6',
        )

    def test_signature_declined_callback(self):
        """Callback view handles DocuSign's 'declined' status."""
        self._test_signature_callback(
            'declined',
            'e9708096-6e41-48e6-b24f-334aadaa93af',
            '9',
        )
