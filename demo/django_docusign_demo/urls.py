from __future__ import unicode_literals

from distutils.version import StrictVersion

import django
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from django_docusign_demo import views

home_view = views.HomeView.as_view()
settings_view = views.SettingsView.as_view()
create_signature_view = views.CreateSignatureView.as_view()
create_signature_template_view = views.CreateSignatureTemplateView.as_view()
signer_view = views.SignerView.as_view()
signer_return_view = views.SignerReturnView.as_view()
signer_canceled_view = views.SignerCanceledView.as_view()
signer_error_view = views.SignerErrorView.as_view()
signer_declined_view = views.SignerDeclinedView.as_view()
signer_signed_view = views.SignerSignedView.as_view()


anysign_patterns = [
    path('signer/<int:pk>/', signer_view, name='signer'),
    path(
        'signer/<int:pk>/return/',
        signer_return_view,
        name='signer_return'
    ),
    path(
        'signer/<int:pk>/canceled/',
        signer_canceled_view,
        name='signer_canceled'
    ),
    path(
        'signer/<int:pk>/error/',
        signer_error_view,
        name='signer_error'
    ),
    path(
        'signer/<int:pk>/declined/',
        signer_declined_view,
        name='signer_declined'
    ),
    path(
        'signer/<int:pk>/signed/',
        signer_signed_view,
        name='signer_signed'
    ),
]

if StrictVersion(django.get_version()) >= StrictVersion('1.10'):
    anysign_patterns = (anysign_patterns, 'anysign')


urlpatterns = [
    path('', home_view, name='home'),
    path('settings/', settings_view, name='settings'),
    path('signature/add/', create_signature_view, name='create_signature'),
    path(
        'signature/add/template/', create_signature_template_view,
        name='create_signature_template'
    ),

    path('', include(anysign_patterns, namespace='anysign')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
