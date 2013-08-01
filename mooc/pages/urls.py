# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from pages import views

# Pages are accessed using the help/<page> syntax. If the 'search' GET parameter
# appears, the page is replaced with a search.
urlpatterns = patterns('',
    url(r'^$', views.view_page, name='help_index'),
    url(r'^(?P<page>[^/]+)/$', views.view_page, name='help'),
)

