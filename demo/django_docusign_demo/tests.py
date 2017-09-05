# coding=utf8
from contextlib import contextmanager
import os
import unittest
import uuid
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock

from django.core.urlresolvers import reverse
import django.test
from django.test.utils import override_settings

from django_docusign import api as django_docusign

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


class DocuSignSettingsTestCase(unittest.TestCase):
    """Tests around ``docusign_settings()`` utility function."""
    def test_easy(self):
        """django_docusign.views.docusign_setting reads conf in session."""
        with temporary_env():
            request = mock.Mock()
            request.session = {'root_url': 'URL',
                               'username': 'NAME',
                               'password': 'PASS',
                               'not related to docusign': 'FOO'}
            os.environ['DOCUSIGN_PASSWORD'] = 'DEFAULT_PASS'
            os.environ['DOCUSIGN_INTEGRATOR_KEY'] = 'INTEGRATOR'
            self.assertEqual(views.docusign_settings(request),
                             {'root_url': 'URL',
                              'username': 'NAME',
                              'password': 'PASS'})


class SettingsViewTestCase(django.test.TestCase):
    """Tests around ``SettingsView``."""
    def test_session_settings(self):
        """SettingsView actually stores settings in session."""
        with temporary_env():
            # 1. Make sure we are using settings from environment.
            os.environ['DOCUSIGN_ROOT_URL'] = 'ENV'
            os.environ['DOCUSIGN_PASSWORD'] = 'ENV'
            home_url = reverse('home')
            response = self.client.get(home_url)
            request = response._request
            self.assertTrue('root_url' not in request.session)
            # 2. POST settings, make sure we use settings in session.
            settings_url = reverse('settings')
            data = {
                'username': 'NAME',
                'password': 'PASS',
                'integrator_key': 'INTEGRATOR',
            }
            response = self.client.post(settings_url, data, follow=True)
            self.assertRedirects(response, home_url)
            request = response._request
            self.assertTrue('root_url' not in request.session)
            self.assertEqual(request.session['username'], 'NAME')
            self.assertEqual(request.session['password'], 'PASS')
            self.assertEqual(request.session['integrator_key'], 'INTEGRATOR')


class SignatureFunctionalTestCase(django.test.TestCase):
    """Functional test suite for signature workflow."""
    #: Class-level signature instance, in order to reduce API calls.
    _signature = None
    pydocusign_create_envelope_method = \
        'pydocusign.DocuSignClient.create_envelope_from_documents'

    @property
    def signature(self):
        """Get or create signature instance."""
        if self._signature is None:
            self._signature = self.create_signature()
        return self._signature

    def create_signature(self):
        url = reverse('create_signature')
        filepath = os.path.join(fixtures_dir, 'test.pdf')
        with open(filepath, 'rb') as document_file:
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
            }
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        return models.Signature.objects.order_by('-pk').first()

    def test_form_valid(self):
        """Can create a signature using 'create_signature' URL."""
        self.assertTrue(self.signature.signature_backend_id)

    def test_create_signature_no_event(self):
        with mock.patch(self.pydocusign_create_envelope_method) \
                as mock_envelope:
            mock_envelope.return_value = str(uuid.uuid4())
            self.assertTrue(self.signature.signature_backend_id)
        envelope = mock_envelope.call_args_list[0][0][0]
        self.assertIsNone(envelope.eventNotification)

    def test_signer_view(self):
        """Signer view redirects to DocuSign."""
        url = reverse('anysign:signer',
                      args=[self.signature.signers.all()[0].pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response['Location'].startswith('https://demo.docusign.net'))

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_canceled(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url, {'event': 'cancel'})
        self.assertFalse(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_canceled', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer.status, 'draft')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_did_nothing(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        mock_recipients.return_value = {
            'signers': [
                {'status': 'sent',
                 'clientUserId': str(signer.pk)}
            ]
        }

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_canceled', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer.status, 'draft')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_authentification_failed(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        mock_recipients.return_value = {
            'signers': [
                {'status': 'sent',
                 'clientUserId': str(signer.pk),
                 'recipientAuthenticationStatus': {
                        'accessCodeResult': {'status': 'Failed'}
                 }}
            ]
        }

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_error', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer.status, 'authentication_failed')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_auto_responded(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        mock_recipients.return_value = {
            'signers': [
                {'status': 'auto_responded',
                 'clientUserId': str(signer.pk)}
            ]
        }

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_error', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer.status, 'auto_responded')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_completed(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        mock_recipients.return_value = {
            'signers': [
                {'status': 'completed',
                 'clientUserId': str(signer.pk)}
            ]
        }

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_signed', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer.status, 'completed')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_return_declined(self, mock_recipients):
        signature = self.create_signature()
        signer = signature.signers.all()[0]

        mock_recipients.return_value = {
            'signers': [
                {'status': 'declined',
                 'clientUserId': str(signer.pk),
                 'declinedReason': u'Jeg ønsker ikke\nå signere.'}
            ]
        }

        url = reverse('anysign:signer_return', args=[signer.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_declined', args=[signer.pk]))
        signature.refresh_from_db()
        signer.refresh_from_db()
        self.assertEqual(signature.status, 'declined')
        self.assertEqual(signer.status, 'declined')
        self.assertEqual(signer.status_details, u'Jeg ønsker ikke\nå signere.')

    @mock.patch('pydocusign.DocuSignClient.get_envelope_recipients')
    def test_signer_all_signed(self, mock_recipients):
        signature = self.create_signature()
        signer1 = signature.signers.all()[0]
        signer2 = signature.signers.all()[1]

        mock_recipients.side_effect = [
            {
                'signers': [
                    {'status': 'completed',
                     'clientUserId': str(signer1.pk)},
                    {'status': 'sent',
                     'clientUserId': str(signer2.pk)}
                ]
            },
            {
                'signers': [
                    {'status': 'completed',
                     'clientUserId': str(signer1.pk)},
                    {'status': 'completed',
                     'clientUserId': str(signer2.pk)}
                ]
            },
        ]

        url = reverse('anysign:signer_return', args=[signer1.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_signed', args=[signer1.pk]))
        signature.refresh_from_db()
        signer1.refresh_from_db()
        signer2.refresh_from_db()
        self.assertEqual(signature.status, 'draft')
        self.assertEqual(signer1.status, 'completed')
        self.assertEqual(signer2.status, 'draft')

        url = reverse('anysign:signer_return', args=[signer2.pk])
        response = self.client.get(url)
        self.assertTrue(mock_recipients.called)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('anysign:signer_signed', args=[signer2.pk]))
        signature.refresh_from_db()
        signer1.refresh_from_db()
        signer2.refresh_from_db()
        self.assertEqual(signature.status, 'completed')
        self.assertEqual(signer1.status, 'completed')
        self.assertEqual(signer2.status, 'completed')


class SignatureTemplateFunctionalTestCase(SignatureFunctionalTestCase):
    """Functional test suite for signature template workflow."""
    pydocusign_create_envelope_method = \
        'pydocusign.DocuSignClient.create_envelope_from_template'

    def create_signature(self):
        url = reverse('create_signature_template')
        response = self.client.get(url)
        # get template_id from initial data
        # must be defined in environment variable DOCUSIGN_TEST_TEMPLATE_ID
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
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        return models.Signature.objects.order_by('-pk').first()


def noop(*args, **kwargs):
    """Noop client factory."""
    return 'noop'


class DocuSignBackendTestCase(unittest.TestCase):
    """Tests around :class:`~django_docusign.backend.DocuSignBackend`."""
    def test_setup_explicit(self):
        """DocuSignBackend() proxies options to DocuSignClient()."""
        explicit_options = {
            'root_url': 'http://example.com',
            'username': 'johndoe',
            'password': 'secret',
            'integrator_key': 'very-secret',
            'account_id': 'some-uuid',
            'app_token': 'some-token',
            'timeout': 300.0,
        }
        backend = django_docusign.DocuSignBackend(**explicit_options)
        for key, value in explicit_options.items():
            self.assertEqual(getattr(backend.docusign_client, key), value)

    def test_setup_settings(self):
        """DocuSignBackend uses settings.DOCUSIGN_*."""
        overrides = {
            'DOCUSIGN_ROOT_URL': 'http://example.com',
            'DOCUSIGN_USERNAME': 'pierre paul ou jacques',
            'DOCUSIGN_PASSWORD': 'not-a-secret',
            'DOCUSIGN_INTEGRATOR_KEY': 'not-an-integator-key',
            'DOCUSIGN_ACCOUNT_ID': 'not-an-uuid',
            'DOCUSIGN_APP_TOKEN': 'not-a-token',
            'DOCUSIGN_TIMEOUT': 200.123,
        }
        with override_settings(**overrides):
            backend = django_docusign.DocuSignBackend()
        for key, value in overrides.items():
            key = key.lower()[len('DOCUSIGN_'):]
            self.assertEqual(getattr(backend.docusign_client, key), value)

    def test_setup_priority(self):
        """Explicit arguments have priority over settings."""
        explicit_options = {
            'root_url': 'http://example.com',
            'username': 'johndoe',
            'password': 'secret',
            'integrator_key': 'very-secret',
            'account_id': 'some-uuid',
            'app_token': 'some-token',
            'timeout': 300.0,
        }
        overrides = {
            'DOCUSIGN_ROOT_URL': 'http://another.example.com',
            'DOCUSIGN_USERNAME': 'pierre paul ou jacques',
            'DOCUSIGN_PASSWORD': 'not-a-secret',
            'DOCUSIGN_INTEGRATOR_KEY': 'not-an-integator-key',
            'DOCUSIGN_ACCOUNT_ID': 'not-an-uuid',
            'DOCUSIGN_APP_TOKEN': 'not-a-token',
            'DOCUSIGN_TIMEOUT': 200.123,
        }
        with override_settings(**overrides):
            backend = django_docusign.DocuSignBackend(**explicit_options)
        for key, value in explicit_options.items():
            self.assertEqual(getattr(backend.docusign_client, key), value)
