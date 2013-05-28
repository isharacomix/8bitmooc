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
    if page is None: return redirect( "help", page="index" )
    if page.lower() != page: return redirect( "help", page.lower() )
    try:
        p = Page.objects.get(name=page)
        LogEntry.log(request)
        return render(request,
                      "help_page.html",
                      {'content': p.content,
                       'title': p.name,
                       'alerts': request.session.pop('alerts', [])})
    except exceptions.ObjectDoesNotExist:
        raise Http404()

