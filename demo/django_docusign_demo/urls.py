from django.conf.urls import patterns, url, include

from django_docusign_demo import views


home_view = views.HomeView.as_view()
settings_view = views.SettingsView.as_view()
create_signature_view = views.CreateSignatureView.as_view()
signer_view = views.SignerView.as_view()
signer_return_view = views.SignerReturnView.as_view()


urlpatterns = patterns(
    '',
    url(r'^$', home_view, name='home'),
    url(r'^settings/$', settings_view, name='settings'),
    url(r'^signature/add/$', create_signature_view, name='create_signature'),
    url(
        r'^signer/(?P<pk>\d+)/',
        include(
            patterns(
                '',
                url(r'^$', signer_view, name='signer'),
                url(r'^return/$', signer_return_view, name='signer_return'),
            ),
            namespace='anysign',
            app_name='anysign',
        ),
    ),
)
