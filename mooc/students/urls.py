# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from students import views

# Student Profile URL pattern - includes the internal "edit profile page".
urlpatterns = patterns('',
    url(r'^user/$', views.user_list, name='users'),
    url(r'^user/(?P<username>[\w-]+)/$', views.user_profile, name='profile'),
    url(r'^sign-in/$', views.sign_in, name='sign-in'),
    url(r'^sign-up/$', views.sign_up, name='sign-up'),
    url(r'^sign-out/$', views.sign_out, name='sign-out'),
)

