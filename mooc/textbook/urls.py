from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from textbook import views

# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^$', views.view_page, name='textbook'),
    url(r'^(?P<page>[a-z0-9-]+)/$', views.view_page, name='textbook_page'),
    url(r'^search/(?P<query>[a-z0-9-]+)$', views.find_pages, name='textbook_search'),
)

