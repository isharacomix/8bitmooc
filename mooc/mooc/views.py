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

from pages.models import Page
from forum.models import DiscussionBoard
from students.models import LogEntry


# On the index, we aggregate the newest posts in the 'news' forum so that
# students can go and comment on them.
def view_index(request):
    try:
        news = []
        for d in DiscussionBoard.objects.get(slug="news").discussiontopic_set.all()[:5]:
            news.append( d.discussionpost_set.all()[0] )
    except: news = []
    
    return render( request, 'index.html', {'news': news,
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


# View the embedded IRC!
def webchat(request):
    LogEntry.log(request, "chat")
    return render(request, "chat.html")

