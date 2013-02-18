from django.conf.urls import patterns, include, url

from badges import views

# These are the URLs for the badges. This provides a RESTful assertion API
# to play nicely with badge verifiers. A logged in user can visit the badge
# page to apply for the badge.
urlpatterns = patterns('',
    url(r'^$', views.list_badges, name='badge_list'),
    url(r'^(?P<badge>[\w-]+)/$', views.view_badge, name='badge_view'),
    url(r'^(?P<badge>[\w-]+)/(?P<user>[\w-]+)/$', views.assert_badge, name='badge_assert'),
)

