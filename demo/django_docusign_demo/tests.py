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
                    'signer_name': u'John Accentué',
                    'signer_email': u'john@example.com',
                    'document': document_file,
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

    def test_signature_sent_callback(self):
        """Callback view handles DocuSign's 'sent' status."""
        url = reverse('anysign:signature_callback')
        request_body = open(
            os.path.join(fixtures_dir, 'callback_sent.xml')).read()
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)

    def test_signature_delivered_callback(self):
        """Callback view handles DocuSign's 'delivered' status."""
        url = reverse('anysign:signature_callback')
        request_body = open(
            os.path.join(fixtures_dir, 'callback_delivered.xml')).read()
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)

    def test_signature_signed_callback(self):
        """Callback view handles DocuSign's 'signed' status."""
        url = reverse('anysign:signature_callback')
        request_body = open(
            os.path.join(fixtures_dir, 'callback_signed.xml')).read()
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)

    def test_signature_declined_callback(self):
        """Callback view handles DocuSign's 'declined' status."""
        url = reverse('anysign:signature_callback')
        request_body = open(
            os.path.join(fixtures_dir, 'callback_declined.xml')).read()
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)
