# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from challenges import views

# Student Profile URL pattern - includes the internal "edit profile page".
urlpatterns = patterns('',
    url(r'^(?P<name>[\w-]+)/$', views.view_challenge, name='challenge'),
    url(r'^(?P<name>[\w-]+)/sos/$', views.view_sos, name='sos'),
    #url(r'^(?P<name>[\w-]+)/feedback/$', views.view_feedback, name='feedback'),
)

