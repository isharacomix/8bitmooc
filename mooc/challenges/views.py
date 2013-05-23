# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from students.models import Student
from challenges.models import Challenge, ChallengeResponse


# This returns a list of challenges for the page to render. Only challenges
# that the user has the prerequisites for are available.
def challenge_list(request):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First get all of the challenges that match the user's level. Then create
    # a challenge list tuple that contains the challenge, whether the challenge
    # has been successfully completed, the records for size and speed, and the
    # number of SOSses.
    challenge_list = []
    complete_set = me.challenge_set.all()[:]
    for c in Challenge.objects.filter(difficulty__lte=me.level):
        if c in complete_set or (not c.expired and (not c.prereq or c.prereq in complete_set)):
            complete = c in complete_set
            size = 0
            speed = 0
            size_complete = False
            speed_complete = False
            sos = 0
            if complete:
                pass # calculate real size and speed and stuff.
            challenge_list.append( (c, complete, size, size_complete, speed, speed_complete, sos) )
    
    # Break the challenges into two columns.
    l1, l2 = len(challenge_list)//2, len(challenge_list)%2
    challenge_columns = ( challenge_list[:l1+l2], challenge_list[l1+l2:] )
    return render( request, "challenge_list.html", {"challenges":challenge_columns,
                                                    'alerts': request.session.pop('alerts', []) })
                   


def view_challenge(request, name):
    me = Student.from_request(request)
    if "alerts" not in request.session: request.session["alerts"] = []
    if not me:
        request.session["alerts"].append(("alert-error","Please sign in first."))
        return redirect("sign-in")   
    
    # First, try to get the challenge.
    try: challenge = Challenge.objects.get(slug=name)
    except exceptions.ObjectDoesNotExist: raise Http404()
    
    # Now make sure that the student can actually see the challenge before
    # letting them look at it. They can see expired challenges, but can't
    # submit to them.
    
    # Display the correct challenge page depending on whether it's autograded
    # or coded.
    if challenge.autograde:
        return render(request, "challenge_asm.html", {'challenge': challenge,
                                                      'alerts': request.session.pop('alerts', []) })
    elif challenge.is_jam:
        return render(request, "challenge_jam.html", {'challenge': challenge,
                                                      'alerts': request.session.pop('alerts', []) })
    else:
        return render(request, "challenge_other.html", {'challenge': challenge,
                                                        'alerts': request.session.pop('alerts', []) })


def badge_details(request, challenge):
    raise Http404()
def badge_assertion(request, challenge, student):
    raise Http404()


