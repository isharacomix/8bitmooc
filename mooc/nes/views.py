# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from assembler.asm import Assembler


# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request, name="untitled"):
    if "rom" in request.session and request.session["rom"] != "":
        response = HttpResponse(request.session["rom"], content_type='application/x-nes-rom')
        response['Content-Disposition'] = 'attachment; filename=%s.nes'%name
        return response 
    else:
        raise Http404()


