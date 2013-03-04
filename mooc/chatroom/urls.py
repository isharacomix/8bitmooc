# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from chatroom import views

# These are the URLs for the badges. This provides a RESTful assertion API
# to play nicely with badge verifiers. A logged in user can visit the badge
# page to apply for the badge.
urlpatterns = patterns('',
    url(r'^$', views.do_chat, name='chat'),
    url(r'^test/$', views.test_chat, name='chat'),
)

