# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from chatroom import views

# Even though this URL isn't user-visible, it serves as the restful interface
# for POST requests by the javascript chat.
urlpatterns = patterns('',
    url(r'^$', views.do_chat, name='chat'),
)

