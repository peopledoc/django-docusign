from django.conf.urls import patterns, url
from django.views.generic import TemplateView


home_view = TemplateView.as_view(template_name='home.html')


urlpatterns = patterns(
    '',
    url(r'^$', home_view, name='home')
)
