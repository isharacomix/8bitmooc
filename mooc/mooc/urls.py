# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

from mooc import views

# This kicks off the admin panel.
admin.autodiscover()

# Point URLs to their respective apps, and be smart about it.
urlpatterns = patterns('',
    url(r'^$', views.view_index, name='index'),
    #url(r'^search/$', views.search, name='search'),
    url(r'^chat/$', views.webchat, name='chat'),
    
    # Apps!
    #url(r'^', include('nes.urls')),
    url(r'^', include('students.urls')),
    #url(r'^', include('challenges.urls')),
    #url(r'^help/', include('pages.urls')),
    #url(r'^forum/', include('forum.urls')),

    # Django-admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

