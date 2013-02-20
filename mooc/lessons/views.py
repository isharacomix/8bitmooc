# Create your views here.

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page
from lessons.models import Lesson


# 
def test(request):
    k = Lesson.objects.get(shortname="testy")
    return HttpResponse( k.challenge.dummychallenge.name )
    
