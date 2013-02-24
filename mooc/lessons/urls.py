from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from lessons import views


# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^(?P<world>[\w-]+)/$', views.world_map, name='world_map'),
    url(r'^(?P<world>[\w-]+)/(?P<stage>[\w-]+)/$', views.view_stage,
                                                   name='stage'),
    url(r'^(?P<world>[\w-]+)/(?P<stage>[\w-]+)/lesson/$', views.view_lesson,
                                                          name='lesson'),
    url(r'^(?P<world>[\w-]+)/(?P<stage>[\w-]+)/challenge/$', views.view_challenge,
                                                             name='challenge'),
)

