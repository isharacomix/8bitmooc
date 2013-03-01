# Create your views here.

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page
from students.models import Student

from assembler.asm import Assembler

import random


# This just displays the playground. No big deal.
def view_playground(request):
    if request.method == 'POST':
        return do_playground(request)
    return render( request, "assembler_playground.html")


# The 'do' method runs when we get the POST request. This compiles the ROM,
# stores it in the DB (even if the student isn't logged in), and stores it
# in the request.session. Whether it reloads the same page or passes the
# file for download 
def do_playground(request):
    code = request.POST["code"]
    a = Assembler()
    rom, errors = a.assemble( code )
    
    # Either run the game in the browser or download it.
    request.session["rom"] = rom
    if "run" in request.POST:
        return render( request, "assembler_playground.html", {"source_code": request.POST["code"]})
    else:
        return get_rom(request)


# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request):
    if "rom" in request.session:
        response = HttpResponse(request.session["rom"], content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="rom.nes"'
        return response 
    else:
        raise Http404()

