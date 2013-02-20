# Create your views here.

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page
from lessons.models import Lesson, Module


# This handles the error handling and getting the proper module and lesson
# from the shortnames.
def get_lesson(module, lesson):
    try:
        mod = Module.objects.get(shortname=module)
        les = Lesson.objects.get(module=mod, shortname=lesson)
        return les
    except: raise Http404()


# We load the lesson which shows the tutorial page in the left column and the
# chat stream (or other social tools) on the right. If no tutorial page exists,
# then we redirect to the challenge.
def view_lesson(request, module, lesson):
    les = get_lesson(module, lesson)
    if not les.tutorial:
        if les.challenge: return redirect( "challenge", module = module, lesson =lesson )
        else: raise Http404()
        
    #TODO log this as read.
    
    return HttpResponse( les.shortname )


# We load the challenge which looks different depending on which challenge
# family we're dealing with (hard-coded).
def view_challenge(request, module, lesson):
    les = get_lesson(module, lesson)
    if not les.challenge:
        if les.tutorial: return redirect( "lesson", module = module, lesson =lesson )
        else: raise Http404()
    
    # TODO log the view
    
    # These are all of the types of challenges.
    c = les.challenge
    if hasattr(c, "quizchallenge"): return view_quizchallenge(request, les,
                                                              c.quizchallenge)
    raise Http404
    

# This is a quizchallenge.
def view_quizchallenge( request, lesson, challenge ):
    return HttpResponse( "boo!" )

