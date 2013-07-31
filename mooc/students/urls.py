# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from students import views

# Student Profile URL pattern - includes the internal "edit profile page".
urlpatterns = patterns('',
    url(r'^oauth/$', views.handle_oauth, name="oauth"),
    url(r'^login/$', views.handle_login, name="login"),
    url(r'^logout/$', views.handle_logout, name="logout"),
    url(r'^terms/$', views.terms_of_use, name="shrinkwrap"),
    url(r'^user/(?P<username>[\w-]+)/$', views.user_profile, name='user_profile'),
)

