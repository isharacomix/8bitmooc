from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from lessons import views

# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^lesson/$', views.test, name='lesson'),
    url(r'^challenge/$', views.test, name='challenge'),
)

