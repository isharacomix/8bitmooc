# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from students import views

# Student Profile URL pattern - includes the internal "edit profile page".
urlpatterns = patterns('',
    url(r'^~(?P<username>[\w-]+)$', views.view_profile, name='profile'),
)

