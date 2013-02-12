from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

#
def index(request):
    return render(request, "index.html", {'title': "ahoy"},
                      status=404)
