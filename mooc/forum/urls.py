# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from forum import views

# Forum url dispatcher
urlpatterns = patterns('',
    url(r'^$', views.board_list, name='forums'),
    url(r'^(?P<name>[\w-]+)/$', views.view_board, name='board'),
    url(r'^(?P<name>[\w-]+)/(?P<thread>[\d]+)/$', views.view_thread, name='thread'),
)

