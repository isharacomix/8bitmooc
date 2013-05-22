# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from pages.models import Page
from students.models import LogEntry


# This method simply passes the string to the appropriate template and renders
# it in markdown.
def view_page(request, page=None):
    if request.GET.get("search"): return redirect( "help", page=request.GET["search"] )
    if page is None: return redirect( "help", page="index" )
    try:
        p = Page.objects.get(name=page)
        LogEntry.log(request)
        return render(request,
                      "help_page.html",
                      {'content': p.content,
                       'title': p.name,
                       'alerts': request.session.pop('alerts', [])})
    except exceptions.ObjectDoesNotExist:
        return find_pages(request, page)


# This function returns a list of tuples in the format (slug, digest). The
# page is responsible for handling that list.
def find_pages(request, query):
    # TODO log the search!
    
    # Go through the text and find a digest that will allow the user to
    # find relevant data.
    pages = Page.objects.filter(content__contains=query)
    results = []
    for p in pages:
        i = p.content.index(query)
        results.append( (p.title,"..."+p.content[max(0,i-50):min(len(p.content),i+50)]+"...") )
    
    LogEntry.log(request, "search")
    return render(request,
                  "help_search.html",
                  {'results': results,
                   'query': query,
                   'alerts': request.session.pop('alerts', []) },
                  status=404)

