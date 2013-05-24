# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from nes import views

# The NES is mostly a back-end thing, however, it has a function called by a
# view that allows it to create and retrieve ROM images.
urlpatterns = patterns('',
    url(r'^rom/$', views.get_rom, name='rom'),
    url(r'^play/(?P<id>[\d]+)/$', views.play_game, name='play'),
    url(r'^playground/$', views.view_playground, name='playground'),
)

