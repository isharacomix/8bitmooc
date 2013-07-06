# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions

from nes.models import Pattern
from students.models import Student


# Challenges fall into three categories: traditional, project-euler style
# challenges that are autograded, "achievements" that are won when outside
# conditions are met, and game jams where the student submits a project to an
# external competition like Ludum Dare, and simply gives us the hyperlink.
class Challenge(models.Model):
    name            = models.CharField("Challenge Name",
                                       unique=True,
                                       max_length=200,
                                       help_text="""Full name of the challenge.""")
    slug            = models.SlugField("Challenge Slug",
                                       unique=True,
                                       help_text="""Short name of the challenge. 
                                       Used in the URL.""")
    description     = models.TextField("Description",
                                       help_text="""Markdown description of the
                                       challenge.""")
    autograde       = models.SlugField("Autograde Function",
                                       blank=True,
                                       help_text="""Specifies the function for
                                       the autograder if this is an autograded 
                                       challenge. If left blank, it must be
                                       manually graded.""")
    preamble        = models.TextField("Preamble",
                                       blank=True,
                                       help_text="""Preamble of an autograded 
                                       challenge.""")
    postamble       = models.TextField("Postamble",
                                       blank=True,
                                       help_text="""Postamble of an autograded
                                       challenge.""")
    pattern         = models.ForeignKey(Pattern,
                                        null=True,
                                        blank=True,
                                        help_text="""The sprite sheet of an
                                        autograded challenge.""")
    completed_by    = models.ManyToManyField(Student,
                                             blank=True,
                                             help_text="""List of all students
                                             who have completed this challenge.""")
    ordering = models.IntegerField("Ordering",
                                   help_text="""Order in which challenges will
                                   appear.""")

    # Representation of the challenge
    def __unicode__(self):
        return u"%s" % (self.name)
    
    # Order these by difficulty.
    class Meta:
        ordering = ['ordering']
    
    
# Challenge Responses are student submissions for Challenges that are either
# jams or autograded.
class ChallengeResponse(models.Model):
    student     = models.ForeignKey(Student,
                                    verbose_name="Student",
                                    null=True,
                                    blank=True,
                                    help_text="""The author of the challenge
                                    response.""")
    challenge   = models.ForeignKey(Challenge,
                                    verbose_name="Challenge",
                                    null=True,
                                    blank=True,
                                    help_text="""The challenge being responded
                                    to. If None, this is a playground
                                    submission.""")
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""The time that the response
                                       was submitted.""")
    parent      = models.ForeignKey("self",
                                    verbose_name="Parent",
                                    null=True,
                                    blank=True,
                                    help_text="""If the Parent is True, it means
                                    that this submission's code is actually a
                                    unified diff. This helps minimize the space
                                    used by code submissions in the code
                                    playground.""")
    code        = models.TextField("Code",
                                   help_text="""This is either the code of an
                                   autograded challenge or the URL of a jam.""")
    is_correct  = models.NullBooleanField("Is Correct",
                                          default=None,
                                          help_text="""When true, this challenge 
                                          was correct. If None, the jam link
                                          hasn't been evaluated yet.""")
    rom_size    = models.IntegerField("ROM size",
                                      default=0xffff,
                                      help_text="""The size of the compiled ROM
                                      of a successful response.""")
    runtime     = models.IntegerField("Running Time",
                                      default=0xffff,
                                      help_text="""The number of steps it takes
                                      to complete the test cases.""")
    
    # Representation of the challenge
    def __unicode__(self):
        return u"Challenge Response %d for %s" % (self.id,
                                                  self.challenge if self.challenge else "Playground")



# SOS: requests for feedback on a submission. It is also possible to create
# "null" SOS requests for grading purposes.
class SOS(models.Model):
    student     = models.ForeignKey(Student,
                                    verbose_name="Student",
                                    help_text="""The student requesting help.""")
    challenge   = models.ForeignKey(Challenge,
                                    verbose_name="Challenge",
                                    help_text="""The challenge that this
                                    request is associated with. This helps us
                                    filter open SOSes, despite being redundant.""")
    submission  = models.ForeignKey(ChallengeResponse,
                                    verbose_name="Challenge Submission",
                                    help_text="""The challenge response that this
                                    request is associated with.""")
    content     = models.TextField("Content",
                                   help_text="""The question being asked by the
                                   student.""")
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""The time that the request
                                       was submitted.""")
    active      = models.BooleanField("Active?",
                                  default=True,
                                  help_text="""An SOS is active until it gets
                                  three feedbacks or until the student submits
                                  a new one for the same challenge.""")

    # Representation of the SOS
    def __unicode__(self):
        return u"SOS %d for %s" % (self.id, self.challenge)


# Feedback for a challenge. Feedback can exist for any challenge, and while it
# is often explicitly tied with an SOS, 
class Feedback(models.Model):
    author      = models.ForeignKey(Student,
                                    verbose_name="Author",
                                    help_text="""The student giving the feedback.""")
    sos         = models.ForeignKey(SOS,
                                    verbose_name="SOS",
                                    help_text="""The SOS being responded to.""")
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""The time that the request
                                       was answered.""")
    content     = models.TextField("Content",
                                   help_text="""The feedback description.""")
    confident   = models.BooleanField("Confident?",
                                      default=False,
                                      help_text="""True if the student giving
                                      the help was confident in their response?""")
    good        = models.BooleanField("Good SOS?",
                                      default=False,
                                      help_text="""True if the student giving
                                      the help thought the question was a good
                                      one.""")
    helpful     = models.NullBooleanField("Helpful?",
                                          help_text="""When a student gets their
                                          feedback, they can then mark it as
                                          helpful or unhelpful.""")
    
    # Representation of the SOS
    def __unicode__(self):
        return u"Feedback: %s" % (self.sos)


