# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student, LogEntry
from challenges.models import Challenge, ChallengeResponse, Badge, SOS, Feedback
from django.contrib.auth.models import User

from nes import assembler
from nes.views import get_rom
from challenges import autograde

import hashlib
import json
import time
import random


# This returns a list of challenges for the page to render. Only challenges
# that the user has the prerequisites for are available.
def challenge_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # Get GET parameters, pagination and filters
    filt = request.GET.get("filter")
    page = request.GET.get("page")
    if page and page.isdigit(): page = max(0, int(page)-1)
    else: page = 0
    pagination = 20 #not used
    
    # First get all of the challenges that match the user's level. Then create
    # a challenge list tuple that contains the challenge, whether the challenge
    # has been successfully completed, the records for size and speed, and the
    # number of SOSses.
    challenge_list = []
    complete_set = me.challenge_set.all()
    for c in Challenge.objects.filter(difficulty__lte=me.level):
        if c in complete_set or (not c.expired and (not c.prereq or c.prereq in complete_set)):
            complete = c in complete_set
            size = 0
            speed = 0
            size_complete = False
            speed_complete = False
            best_size, best_speed = None, None
            my_size, my_speed = None, None
            if complete:
                records = ChallengeResponse.objects.filter(challenge=c, is_correct=True).order_by('-rom_size')
                if len(records) > 0:
                    best_size = records[0].rom_size
                    records = records.order_by('-runtime')
                    best_speed = records[0].runtime
                records = records.filter(student=me).order_by('-rom_size')
                if len(records) > 0:
                    my_size = records[0].rom_size
                    records = records.order_by('-runtime')
                    my_speed = records[0].runtime
            sos = len( SOS.objects.filter(active=True, challenge=c).exclude(student=me) )
            challenge_list.append( (c, complete, my_size, my_size==best_size, my_speed, my_speed==best_speed, sos) )
    
    # Filter challenges.
    filtered_list = []
    if filt == "all":
        filtered_list = challenge_list
    elif filt == "size":
        filtered_list = [c for c in challenge_list if not c[3]]
    elif filt == "speed":
        filtered_list = [c for c in challenge_list if not c[5]]
    elif filt == "sos":
        filtered_list = [c for c in challenge_list if c[6]]
    else:
        filtered_list = [c for c in challenge_list if not c[1]]
        filt = "incomplete"
    
    # Break the challenges into two columns. If we decide to do pagination, do it
    # here.
    l1, l2 = [], []
    for c in filtered_list:
        if len(l1) > len(l2): l2.append(c)
        else: l1.append(c)
    return render( request, "challenge_list.html", {'challenge_columns':(l1,l2),
                                                    'alerts': request.session.pop('alerts', []),
                                                    'filter': filt })
                   

# Display the challenge for the users.
def view_challenge(request, name):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    feedback = len( SOS.objects.filter(challenge=challenge, student=me) )
    
    # Now make sure that the student can actually see the challenge before
    # letting them look at it. They can see expired challenges, but can't
    # submit to them.
    if challenge.difficulty > me.level:
        request.session["alerts"].append(("alert-error",
                                          """You need to reach level %d before
                                          you can attempt this challenge."""%challenge.difficulty))
        return redirect("challenge_list") 
    if challenge.prereq and challenge.prereq not in me.challenge_set.all():
        request.session["alerts"].append(("alert-error",
                                          """You have not unlocked this challenge yet."""))
        return redirect("challenge_list")
    
    # If it was a POST request, then we'll take care of that now. This takes
    # care of the side-effects and creates the challenge responses that will be
    # handled below.
    if request.method == "POST":
        if challenge.autograde: do_asm_challenge(request, me, challenge)
        elif challenge.is_jam: do_jam_challenge(request, me, challenge)
    
    # Display the correct challenge page depending on whether it's autograded
    # or a URL.
    if challenge.autograde:
        if "download" in request.POST:
            good = True
            for e in request.session['alerts']:
                if e[0] == 'alert-error': good = False
            if good: return get_rom(request, challenge.slug)
        else:
            code = ""
            if 'code' in request.POST: code = request.POST['code']
            else:
                subs = ChallengeResponse.objects.filter(student=me).order_by('-timestamp')
                if len(subs) > 0: code = subs[0].code
            
            # Get the record speeds and sizes for everything.
            my_size, my_speed = None, None
            best_size, best_speed = None, None
            completed = False
            
            records = ChallengeResponse.objects.filter(challenge=challenge, is_correct=True).order_by('-rom_size')
            if len(records) > 0:
                best_size = records[0].rom_size
                records = records.order_by('-runtime')
                best_speed = records[0].runtime
            records = records.filter(student=me).order_by('-rom_size')
            if len(records) > 0:
                my_size = records[0].rom_size
                records = records.order_by('-runtime')
                my_speed = records[0].runtime
                completed = True
            
            # Try to load up the best submissions by everyone.
            return render(request, "challenge_asm.html", {'challenge': challenge,
                                                          'alerts': request.session.pop('alerts', []),
                                                          'code': code,
                                                          'my_size': my_size,
                                                          'my_speed': my_speed,
                                                          'best_size': best_size,
                                                          'best_speed': best_speed,
                                                          'completed': completed,
                                                          'badge_domain': settings.ISSUER_DOMAIN,
                                                          'feedback': feedback} )
                                                          
    elif challenge.is_jam:
        # Grey out the submission if the student has already submitted a link for
        # this challenge or if it's expired.
        records = ChallengeResponse.objects.filter(challenge=challenge, student=me)
        url = ""
        submit_ok = True
        completed = me in challenge.completed_by.all()
        if len(records) > 0:
            url = records[0].code
            if records[0].is_correct is not None: submit_ok = False
        if challenge.expired: submit_ok = False
        return render(request, "challenge_jam.html", {'challenge': challenge,
                                                      'alerts': request.session.pop('alerts', []),
                                                      'url': url,
                                                      'submit_ok': submit_ok,
                                                      'completed': completed,
                                                      'badge_domain': settings.ISSUER_DOMAIN,
                                                      'feedback': feedback})
    else:
        completed = me in challenge.completed_by.all()
        return render(request, "challenge_other.html", {'challenge': challenge,
                                                        'alerts': request.session.pop('alerts', []),
                                                        'completed': completed,
                                                        'badge_domain': settings.ISSUER_DOMAIN,
                                                        'feedback': feedback})


# Viewing feedback is easy. Just pass along all of the SOSes and their respective
# feedbacks.
def view_feedback(request, name):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
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
            f = Feedback.objects.get(id=int(f_id))
            if f.sos in feedback and f.helpful is None:
                f.helpful = helpful
                f.save()
                if helpful:
                    f.author.award_xp(50)
                me.award_xp(5)
                LogEntry.log(request, "Marked as %shelpful"%("" if helpful else "un"))

    
    return render(request, "feedback.html", {'challenge': challenge,
                                             'feedback': feedback})
    

# This views the SOSes for a challenge. There are some prerequisites to
# responding to an SOS.
#  * Student must have completed the stage
#  * The student must not have already responded to this SOS
def view_sos(request, name):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    if challenge not in me.challenge_set.all():
        request.session["alerts"].append(("alert-error",
                                          "You must complete this challenge before you can respond to an SOS."))
        return redirect("challenge_list")
    
    # If this is a POST request, we are responding.
    if request.method == "POST":
        if "id" in request.POST and request.POST["id"] == request.session.get("sos-id"):
            target = SOS.objects.get(id=int(request.session.pop("sos-id")))
            fb = Feedback()
            fb.author = me
            fb.sos = target
            fb.content = str(request.POST.get("response"))
            fb.confidence = True if request.POST.get("confident") else False
            fb.good = True if request.POST.get("good") else False
            fb.save()
            
            if (len( target.feedback_set.all() ) >= 3):
                target.active = False
                target.save()
            
            request.session["alerts"].append(("alert-success",
                                              """Thank you for helping your classmates
                                              by participating in the SOS system!
                                              (+10 XP)"""))
            me.award_xp(10)
            LogEntry.log(request, "SOS for %s"%(challenge.slug))
        else:
            request.session["alerts"].append(("alert-error",
                                              """There was an error with your
                                              SOS submission."""))
            LogEntry.log(request, "Botched SOS job.")
        return redirect("challenge_list")
    
    
    # Now find out if there are any SOS requests.
    all_sos = list( SOS.objects.filter(active=True, challenge=challenge).exclude(student=me) )
    if len(all_sos) == 0:
        request.session["alerts"].append(("alert-error",
                                          "There are no active SOS requests for this challenge."))
        return redirect("challenge_list")
    
    # Now find an SOS to respond to. Make sure that we haven't already responded
    # to it.
    random.shuffle( all_sos )
    target = None
    while len(all_sos) > 0 and target is None:
        x = all_sos.pop()
        feedbacks = Feedback.objects.filter( sos=x, author=me )
        if len(feedbacks) == 0:
            target = x
    if target is None:
        request.session["alerts"].append(("alert-error",
                                          "You have already responded to all active SOS requests for this challenge!"))
        return redirect("challenge_list")

    # Filtering is now over. Time to render.
    request.session["sos-id"] = str(target.id)
    if challenge.autograde:
        assembler.assemble_and_store(request, target.submission.code, challenge.pattern,
                                     challenge.preamble, challenge.postamble)
        return render(request, "sos_asm.html", {'challenge': challenge,
                                                'alerts': request.session.pop('alerts', []),
                                                'sos': target } )
    elif challenge.is_jam:
        return redirect("challenge_list")
    else:
        return redirect("challenge_list")
    


# This is a student submission for an ASM challenge. Here we compile the code
# and render it on the display while also doing the autograding.
def do_asm_challenge(request, student, challenge):
    code = request.POST.get("code") if "code" in request.POST else ""
    
    # Save this in the database whether it compiles or not.
    CR = ChallengeResponse()
    CR.student = student
    CR.challenge = challenge
    CR.code = code
    CR.is_correct = False
    CR.save()
    
    # Only try to autograde if the program compiles.
    if assembler.assemble_and_store(request, code, challenge.pattern,
                                    challenge.preamble, challenge.postamble):
        
        completed = student in challenge.completed_by.all()
        results = autograde.grade( challenge, student, code, completed )
        
        # Save its correctness in the database.
        CR.is_correct = True if results else False
        if results: CR.rom_size, CR.runtime = results
        CR.save()
        
        # Award XP if the program is correct.
        if results and not completed:
            challenge.completed_by.add(student)
            challenge.save()
            student.award_xp(challenge.xp)
            student.save()
            request.session['alerts'].append(('alert-success',
                                              '''Congratulations! You completed
                                              this challenge and earned %d
                                              XP.'''%challenge.xp))
            LogEntry.log(request, "Completed %s"%challenge.slug)
        elif results:
            request.session['alerts'].append(('alert-success',
                                              '''This solution was %d bytes in
                                              size and executed %d lines of
                                              code.'''%results))
            LogEntry.log(request, "%s: %d, %d"%(challenge.slug,results[0],results[1]))
    
    # Is there an SOS involved?
    if "sos" in request.POST and "help" in request.POST:
        for s in SOS.objects.filter(challenge=challenge, student=student):
            s.active = False
            s.save()
    
        s = SOS()
        s.challenge = challenge
        s.submission = CR
        s.content = request.POST["help"]
        s.student = student
        s.save()


# Jam Challenges are much simpler - we just submit a URL to the database.
# However, the thing about Jam Challenges is that students only submit a single
# URL for the challenge.
def do_jam_challenge(request, student, challenge):
    code = request.POST.get("url") if "url" in request.POST else ""
    
    # Save this in the database.
    try: CR = ChallengeResponse.objects.get(challenge=challenge, student=student)
    except exceptions.ObjectDoesNotExist:
        CR = ChallengeResponse()
        CR.student = student
        CR.challenge = challenge
        CR.save()
    
    # If the challenge is alrady completed or expired, don't permit changes.
    if challenge.expired or CR.is_correct is not None:
        request.session['alerts'].append(('alert-error',
                                          'This Jam is over - no further changes are permitted.'))
    else:
        CR.code = code
        CR.save()
        request.session['alerts'].append(('alert-success',
                                          'Jam URL updated.'))



# The badge issuer just returns basic information about #8bitmooc in JSON
# format.
def badge_issuer(request):
    badge_issuer_dict = { 
                          "name": settings.ISSUER_NAME,
                          "image": "%s/static/img/logo.png"%settings.ISSUER_DOMAIN,
                          "url": settings.ISSUER_DOMAIN,
                          "email": settings.ISSUER_CONTENT,
                        }
    
    badge_issuer_json = json.dumps(badge_issuer_dict)
    return HttpResponse(badge_assertion_json, content_type='application/json')


# This returns details of the badge itself. Returns 404 unless the challenge
# exists and is_badge is true.
def badge_details(request, challenge):
    try: challenge = Challenge.objects.get(slug=challenge)
    except: raise Http404()
    if not challenge.is_badge: raise Http404()
    
    badge_details_dict = {
                           "name": challenge.name,
                           "description": "Completed the '%s' challenge on #8bitmooc"%challenge.name,
                           "image": "%s/static/img/challenge/%s.png"%(settings.ISSUER_DOMAIN, challenge.graphic),
                           "criteria": "%s/badge/%s/"%(settings.ISSUER_DOMAIN, challenge.slug),
                           "issuer": "%s/badge/"%(settings.ISSUER_DOMAIN)
                         }
    
    badge_details_json = json.dumps(badge_details_dict)
    return HttpResponse(badge_details_json, content_type='application/json')
    

# This returns the badge assertion.
def badge_assertion(request, challenge, student):
    try: challenge = Challenge.objects.get(slug=challenge)
    except: raise Http404()
    if not challenge.is_badge: raise Http404()
    try: student = Student.objects.get( user=User.objects.get(username=student) )
    except: raise Http404()
    if student not in challenge.completed_by.all(): raise Http404()
    try: badge = Badge.objects.get( student=student, challenge=challenge )
    except:
        badge = Badge( student=student, challenge=challenge )
        badge.save()
    
    # Now that we know what's happening...
    if badge.revoked:
        badge_assertion_dict = {"revoked": True}
        badge_assertion_json = json.dumps(badge_assertion_dict)
        return HttpResponse(badge_assertion_json, content_type='application/json', status=410)
    else:
        badge_assertion_dict = {
                                "uid": "%s/%s"%(challenge.slug, student.username),
                                "recipient": {
                                              "type": "email",
                                              "hashed": True,
                                              "salt": settings.BADGE_SALT,
                                              "identity": "sha256$%s"%(hashlib.sha256(student.email+settings.BADGE_SALT).hexdigest())
                                             },
                                "image": "%s/static/img/challenge/%s.png"%(settings.ISSUER_DOMAIN, challenge.graphic),
                                "evidence": settings.ISSUER_DOMAIN,
                                "issuedOn": int(time.mktime(badge.when.timetuple())),
                                "badge": "%s/badge/%s/"%(settings.ISSUER_DOMAIN, challenge.slug),
                                "verify": {
                                           "type": "hosted",
                                           "url": "%s/badge/%s/%s/"%(settings.ISSUER_DOMAIN, challenge.slug, student.username),
                                          }
                               }
        badge_assertion_json = json.dumps(badge_assertion_dict)
        return HttpResponse(badge_assertion_json, content_type='application/json')

