# coding=utf8
from contextlib import contextmanager
import os
import unittest
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock

from django.core.urlresolvers import reverse
import django.test

import pydocusign
import pydocusign.test

from django_docusign_demo import models, views


here = os.path.abspath(os.path.dirname(__file__))
fixtures_dir = os.path.join(here, 'fixtures')


@contextmanager
def temporary_env():
    former_environ = dict(os.environ)  # Backup.
    try:
        yield os.environ
    finally:
        for key, value in former_environ.items():
            os.environ[key] = value  # Restore.


class DocuSignSettingTestCase(unittest.TestCase):
    """Tests around ``docusign_setting()`` utility function."""
    def test_session(self):
        """django_docusign.views.docusign_setting reads conf in session."""
        key = 'fake_key'
        value = 'fake_value'
        request = mock.Mock()
        request.session = {key: value}  # In session.
        self.assertTrue(key not in os.environ)  # Not in environ.
        self.assertEqual(views.docusign_setting(request, key), value)

    def test_environ(self):
        """django_docusign.views.docusign_setting reads env vars."""
        with temporary_env():
            key = 'fake_key'
            value = 'fake_value'
            request = mock.Mock()
            request.session = {}  # Not in session.
            os.environ['PYDOCUSIGN_TEST_FAKE_KEY'] = value  # In environ.
            self.assertEqual(views.docusign_setting(request, key), value)

    def test_fallback(self):
        """django_docusign.views.docusign_setting reads session before env."""
        with temporary_env():
            key = 'fake_key'
            request = mock.Mock()
            request.session = {key: 'session'}  # In session.
            os.environ['PYDOCUSIGN_TEST_FAKE_KEY'] = 'environ'  # In environ.
            self.assertEqual(views.docusign_setting(request, key), 'session')


class DocuSignSettingsTestCase(unittest.TestCase):
    """Tests around ``docusign_settings()`` utility function."""
    def test_easy(self):
        """django_docusign.views.docusign_setting reads conf in session."""
        with temporary_env():
            request = mock.Mock()
            request.session = {'root_url': 'URL',
                               'username': 'NAME',
                               'password': 'PASS'}
            os.environ['PYDOCUSIGN_TEST_PASS'] = 'DEFAULT_PASS'
            os.environ['PYDOCUSIGN_TEST_INTEGRATOR_KEY'] = 'INTEGRATOR'
            self.assertEqual(views.docusign_settings(request),
                             {'root_url': 'URL',
                              'username': 'NAME',
                              'password': 'PASS',
                              'integrator_key': 'INTEGRATOR'})


class SettingsViewTestCase(django.test.TestCase):
    """Tests around ``SettingsView``."""
    def test_session_settings(self):
        """SettingsView actually stores settings in session."""
        with temporary_env():
            # 1. Make sure we are using settings from environment.
            os.environ['PYDOCUSIGN_TEST_ROOT_URL'] = 'ENV'
            home_url = reverse('home')
            response = self.client.get(home_url)
            request = response._request
            self.assertTrue('root_url' not in request.session)
            self.assertEqual(views.docusign_settings(request)['root_url'],
                             'ENV')
            # 2. POST settings, make sure we use settings in session.
            settings_url = reverse('settings')
            api_url = 'http://example.com/root'
            data = {
                'root_url': api_url,
                'username': 'NAME',
                'password': 'PASS',
                'integrator_key': 'INTEGRATOR',
            }
            response = self.client.post(settings_url, data, follow=True)
            self.assertRedirects(response, home_url)
            request = response._request
            self.assertEqual(request.session['root_url'], api_url)
            self.assertEqual(views.docusign_settings(request)['root_url'],
                             api_url)


class SignatureFunctionalTestCase(django.test.TestCase):
    """Functional test suite for signature workflow."""
    #: Class-level signature instance, in order to reduce API calls.
    _signature = None

    @property
    def signature(self):
        """Get or create signature instance."""
        if self._signature is None:
            self._signature = self.create_signature()
        return self._signature

    def create_signature(self):
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
        return models.Signature.objects.order_by('-pk').first()

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

    def send_signature_callback(self, data):
        url = reverse('anysign:signature_callback')
        request_body = pydocusign.test.generate_notification_callback_body(
            data=data)
        response = self.client.post(
            url,
            content_type='text/xml',
            data=request_body,
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_signature_callback(self):
        """Callback view handles DocuSign's 'sent' status."""
        signature = self.create_signature()
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'draft')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'draft')
        signers = signature.signers.all().order_by('signing_order')
        data = {
            "RecipientStatuses": [
                {
                    "Email": signer.email,
                    "UserName": signer.full_name,
                    "ClientUserId": signer.pk,
                    "Status": pydocusign.Recipient.STATUS_SENT,
                    "Sent": "2014-10-06T01:10:01.000012",
                } for signer in signers

            ],
            "EnvelopeId": signature.signature_backend_id,
            "Subject": signature.document_title,
            "UserName": "Bob",
            "Created": "2014-10-06T01:10:00.000012",
            "Sent": "2014-10-06T01:10:01.000012",
        }
        # First, we receive "sent" callback.
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'sent')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'sent')
        # Then, envelope is "delivered" to recipients.
        data['RecipientStatuses'][0]['Status'] = "Delivered"
        data['RecipientStatuses'][0]['Delivered'] = "2014-10-06" \
                                                    "T01:10:02.000012"
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'delivered')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'sent')
        # A recipient signs.
        data['RecipientStatuses'][0]['Status'] = "Signed"
        data['RecipientStatuses'][0]['Signed'] = "2014-10-06" \
                                                 "T01:10:03.000012"
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.status, 'sent')
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'completed')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'sent')
        # Last recipient signs.
        data['RecipientStatuses'][1]['Status'] = "Signed"
        data['RecipientStatuses'][1]['Signed'] = "2014-10-06" \
                                                 "T01:10:04.000012"
        data['Status'] = "Completed"
        data['Completed'] = "2014-10-06T01:10:04.000012"
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.status, 'completed')
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'completed')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'completed')
        # But we could also have received "decline" callback.
        del data['Completed']
        del data['RecipientStatuses'][1]['Signed']
        data['RecipientStatuses'][1]['Status'] = "Declined"
        data['RecipientStatuses'][1]['Declined'] = "2014-10-06" \
                                                   "T01:10:05.000012"
        data['RecipientStatuses'][1]['DeclineReason'] = "Do not sign a test!"
        data['Status'] = "Declined"
        data['Declined'] = "2014-10-06T01:10:05.000012"
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.status, 'declined')
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'completed')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'declined')

        # decline but do not give a reason
        del data['RecipientStatuses'][1]['DeclineReason']
        self.send_signature_callback(data)
        signature = models.Signature.objects.get(pk=signature.pk)
        self.assertEqual(signature.status, 'declined')
        self.assertEqual(signature.signers.get(signing_order=1).status,
                         'completed')
        self.assertEqual(signature.signers.get(signing_order=2).status,
                         'declined')


class SignatureTemplateFunctionalTestCase(SignatureFunctionalTestCase):
    """Functional test suite for signature workflow."""

    def create_signature(self):
        url = reverse('create_signature_template')
        response = self.client.get(url)
        # get template_id from initial data
        # must be defined in environment variable PYDOCUSIGN_TEST_TEMPLATE_ID
        template_id = response.context['form'].initial['template_id']
        data = {
            'signers-TOTAL_FORMS': u'2',
            'signers-INITIAL_FORMS': u'0',
            'signers-MAX_NUM_FORMS': u'1000',
            'signers-0-name': u'John Accentué',
            'signers-0-email': u'john@example.com',
            'signers-1-name': u'Paul Doe',
            'signers-1-email': u'paul@example.com',
            'template_id': template_id,
            'title': u'A very simple PDF document',
            'callback_url': u'http://tech.novapost.fr',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        return models.Signature.objects.order_by('-pk').first()
