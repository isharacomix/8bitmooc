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
from world.models import Stage, World

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
    ACR.name = "untitled"
    if "name" in request.POST:
        ACR.name = ""
        for c in request.POST["name"][:40].lower():
            if c in "abcdefghijklmnopqrstuvwxyz0123456789-_":
                ACR.name += c
    if "public" in request.POST and request.POST["public"]=="True":
        ACR.public = True
    ACR.save()
    
    # Either run the game in the browser or download it.
    request.session["rom"] = rom
    alerts = []
    for e in errors:
        alerts.append( {"tags":"alert-error",
                        "content":e} )
    if "run" in request.POST or len(errors)>0:
        return render( request, "assembler_playground.html", {"name": ACR.name,
                                                              "source_code": code,
                                                              "alerts": alerts})
    else:
        return get_rom(request)


# This retrieves all of the games in the library and sorts them by owner.
def view_library(request):
    games = {}
    
    for g in AssemblyChallengeResponse.objects.filter(public=True,
                                                      challenge=None).reverse():
        if (g.student.username, g.name) not in games:
            games[(g.student.username,g.name)] = g
    
    return render( request, "library.html", {"games": games.values() } )


# This just returns the games for the specified user.
def view_user_library(request, username):
    try:
        student = Student.objects.get( user=User.objects.get(username=username) )
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    games = {}
    for g in AssemblyChallengeResponse.objects.filter(public=True,
                                                      challenge=None,
                                                      student=student).reverse():
        if (g.student.username, g.name) not in games:
            games[(g.student.username,g.name)] = g
    
    return render( request, "library.html", {"games": games.values(),
                                             "username": username } )


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
    return render( request, "assembler_playground.html", {"name":gamename,
                                                          "source_code": code,
                                                          "alerts": alerts})


# The get_rom view simply returns the current ROM that is in the session
# variables.
def get_rom(request):
    if "rom" in request.session and request.session["rom"] != "":
        response = HttpResponse(request.session["rom"], content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="rom.nes"'
        return response 
    else:
        raise Http404()


# The view for an assembly challenge. Invoked by world.assemblychallenge
def view_assemblychallenge(request, world, stage, challenge):
    here = Stage.get_stage(world, stage)
    if request.method == 'POST':
        return do_assemblychallenge(request, world, stage, challenge)
        return redirect("challenge", world = world, stage = stage)

    return render( request, "assembly_challenge.html",
               {
                'world': here.world,
                'stage': here,
                } )

# This is where POST requests are done.
def do_assemblychallenge( request, world, stage, challenge ):
    here = Stage.get_stage(world, stage)
    if not here.challenge:
        if here.tutorial: return redirect( "lesson", world = world, stage =stage )
        else: raise Http404()
    quizID = request.POST.get("quizID")
    challenge, answer_map = request.session.get(quizID)

