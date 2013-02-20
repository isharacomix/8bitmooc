from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from lessons import views

# Textbook URL pattern.
urlpatterns = patterns('',
    url(r'^lesson/(?P<module>[\w-]+)/(?P<lesson>[\w-]+)/$', views.view_lesson,
                                                            name='lesson'),
    url(r'^challenge/(?P<module>[\w-]+)/(?P<lesson>[\w-]+)/$', views.view_challenge,
                                                               name='challenge'),
)

