# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from challenges import views

# Student Profile URL pattern - includes the internal "edit profile page".
urlpatterns = patterns('',
    url(r'^challenge/$', views.challenge_list, name='challenge_list'),
    url(r'^challenge/(?P<name>[\w-]+)/$', views.view_challenge, name='challenge'),
    url(r'^badge/$', views.badge_issuer, name='badge_issuer'),
    url(r'^badge/(?P<challenge>[\w-]+)/$', views.badge_details, name='badge_details'),
    url(r'^badge/(?P<challenge>[\w-]+)/(?P<student>[\w-]+)/$', views.badge_assertion, name='badge_assertion'),
)

