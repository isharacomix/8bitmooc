# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from assembler import views

# The assembler has lots of top-level URLs.
urlpatterns = patterns('',
    url(r'^playground/$', views.view_playground, name='playground'),
    url(r'^rom/$', views.get_rom, name='rom'),
    url(r'^library/$', views.view_library, name='view_library'),
    url(r'^library/(?P<username>[\w-]+)/$', views.view_user_library, name='user_library'),
    url(r'^library/(?P<username>[\w-]+)/(?P<gamename>[\w-]+)/$', views.get_library_game, name='library'),
)

