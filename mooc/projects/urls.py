# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from projects import views

# 
urlpatterns = patterns('',
    url(r'^$', views.project_list, name='project_list'),
    url(r'^(?P<id>[\d]+)/$', views.view_project, name='project'),
)

