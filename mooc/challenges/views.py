# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student, LogEntry
from challenges.models import Challenge
from nes.models import CodeSubmission
from django.contrib.auth.models import User

from nes import assembler
from nes.views import get_rom
from challenges import autograde

import difflib
import random


# Display the challenge for the users.
@Student.permission
def view_challenge(request, name):
    me = Student.from_request(request)
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
        
    # Find the records for this submission. We need them whether we are viewing
    # or processing.
    my_size, my_speed = 0x10000, 0x10000
    best_size, best_speed = 0x1000000, 0x1000000
    completed = False
    records = CodeSubmission.objects.filter(challenge=challenge, is_correct=True).order_by('rom_size')
    if len(records) > 0:
        best_size = records[0].rom_size
        records = records.order_by('runtime')
        best_speed = records[0].runtime
    records = records.filter(student=me).order_by('rom_size')
    if len(records) > 0:
        my_size = records[0].rom_size
        records = records.order_by('runtime')
        my_speed = records[0].runtime
        completed = True
        
    # If it was a POST request, then we'll take care of that now. This takes
    # care of the side-effects and creates the challenge responses that will be
    # handled below.
    code = ""
    if request.method == "POST":
        try: old = CodeSubmission.objects.filter(student=me, challenge=challenge).order_by('-timestamp')[0]
        except: old = None
        
        code = request.POST.get("code") if "code" in request.POST else ""
        CR = CodeSubmission()
        CR.student = me
        CR.challenge = challenge
        CR.code = code
        CR.is_correct = False
        CR.save()
        
        # Convert the last code submission into a diff image, but only save it
        # if the diff is actually smaller than the full code.
        #TODO if the old has an sos attached, then 
        if old:
            old.parent = CR
            old_code = old.code
            old.code = ""
            for d in difflib.unified_diff( old_code.splitlines(), CR.code.splitlines()):
                old.code += d + "\n"
            if len(old.code) < len(old_code):
                old.save()
        
        # Only try to autograde if the program compiles.
        if assembler.assemble_and_store(request, "challenge", code, challenge.pattern,
                                        challenge.preamble, challenge.postamble):
            completed = me in challenge.completed_by.all()
            results = autograde.grade( challenge, me, code, completed )
            
            # Save its correctness in the database.
            CR.is_correct = True if results else False
            if results: CR.rom_size, CR.runtime = results
            CR.save()
            
            # Award XP if the program is correct.
            if results and not completed:
                challenge.completed_by.add(me)
                challenge.save()
                request.session['alerts'].append(('alert-success',
                                                  '''Congratulations! You completed
                                                  this challenge! Can you make it
                                                  more efficient?'''))
                LogEntry.log(request, "Completed %s"%challenge.slug)
            elif results:
                request.session['alerts'].append(('alert-success',
                                                  '''This solution was %d bytes in
                                                  size and executed %d instructions.'''%results))
                LogEntry.log(request, "%s: %d, %d"%(challenge.slug,results[0],results[1]))
            
            if "download" in request.POST:
                return redirect("rom")
            else:
                return redirect("challenge", challenge.slug)
    
    # Load the latest submission code to display it on the screen.
    subs = CodeSubmission.objects.filter(student=me, challenge=challenge).order_by('-timestamp')
    if len(subs) > 0: code = subs[0].code
    
    # Try to load up the best submissions by everyone.
    return render(request, "challenge.html", {'challenge': challenge,
                                              'alerts': request.session.pop('alerts', []),
                                              'code': code,
                                              'my_size': my_size,
                                              'my_speed': my_speed,
                                              'best_size': best_size,
                                              'best_speed': best_speed,
                                              'completed': completed} )

