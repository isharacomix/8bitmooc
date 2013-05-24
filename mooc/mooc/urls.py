# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

from mooc import views

# This kicks off the admin panel.
admin.autodiscover()

# Point URLs to their respective apps, and be smart about it.
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mooc.views.home', name='home'),
    # url(r'^mooc/', include('mooc.foo.urls')),
    
    # Basic pages.
    url(r'^$', views.view_index, name='index'),
    
    url(r'^project/', views.view_index, name='project_list'),
    url(r'^project/(?P<name>[\w-]+)/', views.view_index, name='project'),
    url(r'^forum/', views.view_index, name='forum'),

    # Apps!
    url(r'^', include('nes.urls')),
    url(r'^', include('students.urls')),
    url(r'^', include('challenges.urls')),
    url(r'^help/', include('pages.urls')),

    # Django-admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

