from django.conf.urls import patterns, include, url
from django.contrib import admin

# This kicks off the admin panel.
admin.autodiscover()

# Base URL patterns. The rule is that except for "front", these go to their
# respective apps.
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mooc.views.home', name='home'),
    # url(r'^mooc/', include('mooc.foo.urls')),
    
    # The 'front' app is just for the index.
    url(r'^$', include('front.urls')),

    # Django-admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

