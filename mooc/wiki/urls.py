# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from wiki import views

# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^$', views.view_page, name='textbook'),
    url(r'^(?P<page>[^/]+)/$', views.view_page, name='textbook_page'),
)

