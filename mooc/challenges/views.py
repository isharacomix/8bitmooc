# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student, LogEntry
from challenges.models import Challenge, SOS, Feedback
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
        if old and len(SOS.objects.filter(submission=old)) == 0:
            old.parent = CR
            old_code = old.code
            old.code = ""
            for d in difflib.unified_diff( old_code.splitlines(), CR.code.splitlines()):
                old.code += d + "\n"
            if len(old.code) < len(old_code):
                old.save()
        
        # Only try to autograde if the program compiles.
        compiles = assembler.assemble_and_store(request, "challenge%s"%challenge.slug,
                   code, challenge.pattern, challenge.preamble, challenge.postamble)
        if compiles and challenge.autograde:
            completed = me in challenge.completed_by.all()
            results = autograde.grade( challenge, me, code, completed )
            
            # Save its correctness in the database.
            CR.is_correct = True if results else False
            if results: CR.rom_size, CR.runtime = results
            CR.save()
            
            # Award victory if the program is correct.
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
        
        # Is there an SOS involved?
        if "sos" in request.POST and "help" in request.POST:
            for s in SOS.objects.filter(challenge=challenge, student=me):
                s.active = False
                s.save()
        
            s = SOS()
            s.challenge = challenge
            s.submission = CR
            s.content = request.POST["help"]
            s.student = me
            s.save()
        
        # Handle the redirect.
        if "download" in request.POST and compiles:
            return redirect("rom")
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
                                              'completed': completed,
                                              'feedback': SOS.objects.filter(challenge=challenge, student=me) } )


# This views the SOSes for a challenge. There are some prerequisites to
# responding to an SOS.
#  * Student must have completed the stage
#  * The student must not have already responded to this SOS
@Student.permission
def view_sos(request, name):
    me = Student.from_request(request)
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # Make sure the student has completed it.
    if challenge not in me.challenge_set.all() and not me.ta:
        request.session['alerts'].append(('alert-error',
                                          '''You can't respond to SOS requests
                                          until you complete the challenge!'''))
        return redirect("index")
    if not challenge.autograde and not me.ta:
        request.session['alerts'].append(('alert-error',
                                          '''Only instructors and TAs can grade
                                          code submission projects.'''))
        return redirect("index")
    
    
    # If this is a POST request, we are responding.
    if request.method == "POST":
        if "id" in request.POST and request.POST["id"] == request.session.get("sos-id"):
            target = SOS.objects.get(id=int(request.session.pop("sos-id")))
            fb = Feedback()
            fb.author = me
            fb.sos = target
            fb.content = str(request.POST.get("response"))
            fb.confident = True if request.POST.get("confident") else False
            fb.good = True if request.POST.get("good") else False
            fb.save()
            
            if request.POST.get("pass") and me.ta:
                target.active = False
                target.save()
                target.submission.correct = True
                challenge.completed_by.add( target.student )
                target.submission.save()
                challenge.save()
            
            if (len( target.feedback_set.all() ) >= 3):
                target.active = False
                target.save()
            
            request.session["alerts"].append(("alert-success",
                                              """Thank you for helping your classmates
                                              by participating in the SOS system!"""))
        else:
            request.session["alerts"].append(("alert-error",
                                              """There was an error with your
                                              SOS submission."""))
            LogEntry.log(request, "Botched SOS job.")
        return redirect("index")
    
    
    # Find all of the SOS requests for this challenge.
    all_sos = list( SOS.objects.filter(active=True, challenge=challenge).exclude(student=me) )
    if len(all_sos) == 0:
        request.session["alerts"].append(("alert-error",
                                          "There are no active SOS requests for this challenge."))
        return redirect("index")
    
    # Get a random challenge if you are not the TA. If you're the TA, get the
    # oldest one.
    if not me.ta: random.shuffle( all_sos )
    target = None
    while len(all_sos) > 0 and target is None:
        x = all_sos.pop(0)
        feedbacks = Feedback.objects.filter( sos=x, author=me )
        if len(feedbacks) == 0:
            target = x
    if target is None:
        request.session["alerts"].append(("alert-error",
                                          "You have already responded to all active SOS requests for this challenge!"))
        return redirect("index")
    
    # Now try to assemble the game and then load the page so that we can try to
    # help!
    request.session["sos-id"] = str(target.id)
    assembler.assemble_and_store(request, "challenge", target.submission.code, challenge.pattern,
                                 challenge.preamble, challenge.postamble)
    return render(request, "sos.html", {'challenge': challenge,
                                        'alerts': request.session.pop('alerts', []),
                                        'sos': target } )
    

# Viewing feedback is easy. Just pass along all of the SOSes and their respective
# feedbacks.
@Student.permission
def view_feedback(request, name):
    me = Student.from_request(request)
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # Now get all of the SOSses related to this user and challenge.
    feedback = SOS.objects.filter(challenge=challenge, student=me)
    
    # Mark feedback as helpful or not.
    if "helpful" in request.GET or "unhelpful" in request.GET:
        helpful = True
        if "unhelpful" in request.GET: helpful = False
        f_id = request.GET["helpful" if helpful else "unhelpful"]
        if f_id.isdigit():
            try:
                f = Feedback.objects.get(id=int(f_id))
                if f.sos in feedback and f.helpful is None:
                    f.helpful = helpful
                    f.save()
                    LogEntry.log(request, "Marked as %shelpful"%("" if helpful else "un"))
            except exceptions.ObjectDoesNotExist:
                LogEntry.log(request, "Feedback voting naughtiness.")
    
    return render(request, "feedback.html", {'challenge': challenge,
                                             'feedback': feedback})

