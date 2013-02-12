from django.conf.urls import patterns, url

from front import views

# The front app is a dummy app that lets us control the home page.
# It might be a blog or it might just be an advertisement. Haven't
# decided yet.
urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)

