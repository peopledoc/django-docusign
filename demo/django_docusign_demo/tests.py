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
                'signer_return_url': 'http://example.com/',
                'callback_url': 'http://example.com/',
            }
            response = self.client.post(settings_url, data, follow=True)
            self.assertRedirects(response, home_url)
            request = response._request
            self.assertEqual(request.session['root_url'], api_url)
            self.assertEqual(views.docusign_settings(request)['root_url'],
                             api_url)


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
