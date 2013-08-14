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

from students.models import Student, LogEntry
from challenges.models import Challenge
from forum.models import DiscussionBoard, DiscussionTopic, DiscussionPost
from pages.models import Page


# This views the home page. If the user is logged in, we redirect to the
# dashboard. This is non-dynamic.
def view_index(request):
    me = Student.from_request(request)
    
    if me and me.banned:
        logout(request)
        if "alerts" not in request.session: request.session["alerts"] = []
        request.session["alerts"].append(("alert-error","""This account has
                                          been suspended. If you believe this
                                          is in error, please contact the site
                                          administrator."""))
        return redirect("index")
    elif me and not me.agreed: return redirect("terms")
    elif me: return view_dashboard(request, me)
    
    return render(request,
                  "index.html",
                  {'alerts': request.session.pop('alerts', []) })
    

# This is the dashboard for the student (or TA!). This displays the news and
# announcements on the left side of the page, the remaining challenges on the
# right, and all of the buttons to other locations in the site.
def view_dashboard(request, me):
    announcements = []
    try:
        board = DiscussionBoard.objects.get(slug="news")
        topics = list(DiscussionTopic.objects.filter(board=board, hidden=False))[:5]
        for t in topics:
            announcements.append( (DiscussionPost.objects.filter(topic=t, hidden=False)[0]) )
    except: pass
    return render(request,
                  "dashboard.html",
                  {'challenges': Challenge.show_for(me),
                   'announcements': announcements,
                   'alerts': request.session.pop('alerts', []) })


# Searching!
def search(request):
    me = Student.from_request(request)
    LogEntry.log(request, "search for %s"%request)
    if "query" not in request.GET:
        return redirect("index")
    query = request.GET["query"]
    
    # Filter!
    pages = Page.objects.filter(content__icontains=query)
    results = []
    for p in pages:
        i = p.content.lower().index(query.lower())
        results.append( (p.name,"..."+p.content[max(0,i-50):min(len(p.content),i+50)]+"...") )
    
    # TODO search through forum posts
    return render(request,
                  "search.html",
                  {'results': results,
                   'query': query,
                   'alerts': request.session.pop('alerts', []) })


# View the embedded IRC!
@Student.permission
def webchat(request):
    me = Student.from_request(request)
    LogEntry.log(request, "chat")
    return render(request, "chat.html")

