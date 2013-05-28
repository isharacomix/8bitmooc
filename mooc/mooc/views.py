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

from pages.models import Page
from students.models import LogEntry


# Display the website index. We have to parse the blog feed for this.
def view_index(request):
    try:    feed = feedparser.parse(r'http://blog.8bitmooc.org/rss').entries[:3]
    except: feed = []
    
    return render( request, 'index.html', {'feed': feed,
                                           'alerts': request.session.pop('alerts', []) } )
    

# This function returns a list of tuples in the format (slug, digest). The
# page is responsible for handling that list.
def search(request):
    query = ""
    if "query" in request.GET:
        query = request.GET["query"]
    
    # Go through the text and find a digest that will allow the user to
    # find relevant data.
    pages = Page.objects.filter(content__icontains=query)
    results = []
    for p in pages:
        i = p.content.index(query)
        results.append( (p.name,"..."+p.content[max(0,i-50):min(len(p.content),i+50)]+"...") )
    
    # TODO search through forum posts and games too
    
    LogEntry.log(request, "search")
    return render(request,
                  "search.html",
                  {'results': results,
                   'query': query,
                   'alerts': request.session.pop('alerts', []) })


