# -*- coding: utf-8 -*-

# This file does the autograding for 8bitmooc. Each function is associated with
# a challenge. These challenges handle the grading, point awarding, etc.
# An autograded assignment should take the student's submission and compile
# it. It will award points based on whether or not the assignment was completed
# before.

from django.core import exceptions
from assembler.models import Kernal, Pattern


# Test autograded assignment.
def test(challenge, student, code, completed):
    return "You always pass this assignment"


# This function actually runs the autograder, mapping strings to functions.
# It essentially returns True if the assignment was successful, and it also
# does a bunch of side effects when successful as well.
def grade(challenge, student, code, completed):
    AUTOGRADE_FUNCTIONS = {
                            "test": test
                          }
    if challenge.autograde in AUTOGRADE_FUNCTIONS:
        func = AUTOGRADE_FUNCTIONS[challenge.autograde]
        return func(challenge, student, code, completed)
    else:
        return None


    
