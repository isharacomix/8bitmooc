# Create your views here.

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page
from lessons.models import Lesson, Module

import random


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
    return render( request, "lessons/tutorial.html",
                   {'content': les.tutorial.content,
                    'module': module,
                    'lesson': lesson } )


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
    if hasattr(c, "quizchallenge"): return view_quizchallenge(request,
                                                              module,
                                                              lesson,
                                                              c.quizchallenge)
    raise Http404()


# This processes the quizchallenge and creates a QuizChallengeResponse for the
# user.
def process_quizchallenge( request, module, lesson, challenge ):
    les = get_lesson(module, lesson)
    if not les.challenge:
        if les.tutorial: return redirect( "lesson", module = module, lesson =lesson )
        else: raise Http404()


# This is a quizchallenge. This is pretty tricky to do since we have to be able
# to randomize the quizzes for the user without revealing any of the internal
# structure. To do so, we keep all of the models in the session parameter
# so we can map between the users choices to what they 'really are'.
def view_quizchallenge( request, module, lesson, challenge ):
    if request.method == 'POST':
        if verify_quizchallenge(request, module, lesson, challenge):
            return redirect("challenge", module = module, lesson = lesson)
    
    # Questions is a list of tuples containing
    # (question, multi-choice?, [choiceA, choiceB...])
    answer_map = {}
    question_map = {}
    i = 0
    for q in challenge.questions.order_by('ordering'):
        content = q.question
        choice_map = {}
        choice_map["a"] = q.choiceA
        choice_map["b"] = q.choiceB
        choice_map["c"] = q.choiceC
        choice_map["d"] = q.choiceD
        choice_map["e"] = q.choiceE
        
        # Here we add our choices and (optionally) shuffle them.
        choices = []
        if choice_map["a"]: choices.append("a")
        if choice_map["b"]: choices.append("b")
        if choice_map["c"]: choices.append("c")
        if choice_map["d"]: choices.append("d")
        if choice_map["e"]: choices.append("e")
        if q.random_ok: random.shuffle(choices)
        choice_content = []
        choice_letters = ["a","b","c","d","e"]
        for c in choices:
            choice_content.append( (choice_letters.pop(0), choice_map[c]) )
        
        # Here we map the displayed choices (keys) to the actual database
        # choices (value).
        choices += ["","","","",""]
        choice_map["a"] = choices[0]
        choice_map["b"] = choices[1]
        choice_map["c"] = choices[2]
        choice_map["d"] = choices[3]
        choice_map["e"] = choices[4]
        
        # Save this in the answer map and increment the counter.
        answer_map[i] = (q.question, choice_map)
        question_map[i] = (content, i, q.multiple_ok, choice_content)
        i += 1
        
    # Now the answer_map has been built, we decide whether or not we shuffle it.
    answers = list(range(len(answer_map)))
    if challenge.randomize: random.shuffle(answers)
    
    # We create our questions list and pass them on to the user.
    questions = []
    for a in answers:
        questions.append( question_map[a] )
    
    # Store the answer_map in a session parameter. The session parameter will
    # be passed back with the quiz so that we can 
    formID = "quiz%d"%random.randint(1,1000000)
    request.session[formID] = answer_map

    # Phew! Now render that bad boy!
    return render( request, "lessons/quiz_challenge.html",
                   {'content': challenge.content,
                    'questions': questions,
                    'module': module,
                    'lesson': lesson,
                    'formID': formID } )

