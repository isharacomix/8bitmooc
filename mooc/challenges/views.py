# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect


def challenge_list(request):
    raise Http404()
def view_challenge(request, name):
    raise Http404()
def badge_details(request, challenge):
    raise Http404()
def badge_assertion(request, challenge, student):
    raise Http404()


