# -*- coding: utf-8 -*-
# Create your views here.

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from wiki.models import Page
from students.models import Student

from assembler.asm import Assembler
from assembler.models import AssemblyChallengeResponse
from students.models import Student
from django.contrib.auth.models import User

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
    
    # Save this in the database.
    ACR = AssemblyChallengeResponse()
    try: ACR.student = Student.from_request(request)
    except exceptions.ObjectDoesNotExist: pass
    ACR.code = code
    ACR.save()
    
    # Either run the game in the browser or download it.
    request.session["rom"] = rom
    alerts = []
    for e in errors:
        alerts.append( {"tags":"alert-error",
                        "content":e} )
    if "run" in request.POST or len(errors)>0:
        return render( request, "assembler_playground.html", {"source_code": code,
                                                              "alerts": alerts})
    else:
        return get_rom(request)


# This retrieves a game from the library and displays it in the playground.
def get_library_game(request, username, gamename):
    subs = []
    alerts = []
    try:
        user = User.objects.get(username=username)
        stud = Student.objects.get(user=user)
        
        # If the user is requesting his own games, then we look for any
        # matches. If not, we only look for publicly released games.
        if user == request.user:
            subs = AssemblyChallengeResponse.objects.filter(student=stud,
                                                            name=gamename,
                                                            challenge=None).reverse()
        else:
            subs = AssemblyChallengeResponse.objects.filter(student=stud,
                                                            name=gamename,
                                                            challenge=None,
                                                            public=True).reverse()
    except exceptions.ObjectDoesNotExist: alerts = [{"tags":"alert-error",
                                                     "content":"No such game was found in the library."}]
    
    # TODO: Log the fact that this game was loaded.
    
    # Now try to load the code and compile it.
    code = ""
    if len(subs) > 0: code = subs[0].code
    else: alerts = [{"tags":"alert-error",
                     "content":"No such game was found in the library."}]
    a = Assembler()
    rom, errors = a.assemble( code )
    
    # Set the rom session parameter and run the ROM (or show us the errors).
    request.session["rom"] = rom
    for e in errors:
        alerts.append( {"tags":"alert-error",
                        "content":e} )
    return render( request, "assembler_playground.html", {"source_code": code,
                                                          "alerts": alerts})


# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request):
    if "rom" in request.session:
        response = HttpResponse(request.session["rom"], content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="rom.nes"'
        return response 
    else:
        raise Http404()

