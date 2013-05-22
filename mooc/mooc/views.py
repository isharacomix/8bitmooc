# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

import feedparser


# Display the website index. We have to parse the blog feed for this.
def view_index(request):
    try:    feed = feedparser.parse(r'http://blog.8bitmooc.org/rss').entries[:3]
    except: feed = []
    
    return render( request, 'index.html', {'feed': feed,
                                           'alerts': request.session.pop('alerts', []) } )
    
