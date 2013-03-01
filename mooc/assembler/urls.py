# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from assembler import views


# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^playground/$', views.view_playground, name='playground'),
    url(r'^rom/$', views.get_rom, name='rom'),
)

