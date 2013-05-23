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
                                       help_text="""
                                       Full name of the challenge.
                                                 """)
    slug            = models.SlugField("Challenge Slug",
                                       unique=True,
                                       help_text="""
                                       Short name of the challenge. Used in the
                                       URL.
                                                 """)
    graphic         = models.SlugField("Graphic",
                                       help_text="""
                                       The graphic for the challenge. Should be
                                       a 128x128 PNG.
                                                 """)
    difficulty      = models.IntegerField("Difficulty Level",
                                          help_text="""
                                          Level a player should be before
                                          attempting this challenge.
                                                    """)
    xp              = models.IntegerField("XP Awarded",
                                          help_text="""
                                          XP awarded by completing this
                                          challenge.
                                                    """)
    prereq          = models.ForeignKey("Challenge",
                                        null=True,
                                        blank=True,
                                        help_text="""
                                        Optional prerequisite for the challenge.
                                                  """)
    is_badge        = models.BooleanField("Is Badge",
                                          default=False,
                                          help_text="""
                                          When true, this challenge can be
                                          exported as a Mozilla Open Badge.
                                                    """)
    description     = models.TextField("Description",
                                       help_text="""
                                       Markdown description of the challenge.
                                                 """)
    autograde       = models.SlugField("Autograde Function",
                                       blank=True,
                                       help_text="""
                                       Specifies the function for the autograder
                                       if this is an autograded challenge. If
                                       left blank, this is more like an
                                       achievement that is accomplished in the
                                       rest of the MOOC.
                                                 """)
    is_jam          = models.BooleanField("Is Jam",
                                          default=False,
                                          help_text="""
                                          When true, this challenge is
                                          beaten by submitting a link to an
                                          externally hosted game jam, like
                                          Ludum Dare.
                                                    """)
    preamble        = models.TextField("Preamble",
                                       blank=True,
                                       help_text="""
                                       Preamble of an autograded challenge.
                                                 """)
    postamble       = models.TextField("Postamble",
                                       blank=True,
                                       help_text="""
                                       Postamble of an autograded challenge.
                                                 """)
    pattern         = models.ForeignKey(Pattern,
                                        null=True,
                                        blank=True,
                                        help_text="""
                                        The sprite sheet of an autograded challenge.
                                                  """)
    completed_by    = models.ManyToManyField(Student,
                                             blank=True,
                                             help_text="""
                                             List of all students who have
                                             completed this challenge.
                                                       """)
    expired         = models.BooleanField("Is Expired",
                                          default=False,
                                          help_text="""
                                          When true, this challenge will accept
                                          no further submissions.
                                                    """)

    # Representation of the challenge
    def __unicode__(self):
        return u"%s" % (self.name)


# Challenge Responses are student submissions for Challenges that are either
# jams or autograded.
class ChallengeResponse(models.Model):
    student     = models.ForeignKey(Student,
                                    verbose_name="Student",
                                    null=True,
                                    blank=True,
                                    help_text="""
                                    The author of the challenge response.
                                              """)
    challenge   = models.ForeignKey(Challenge,
                                    verbose_name="Challenge",
                                    null=True,
                                    blank=True,
                                    help_text="""
                                    The challenge being responded to. If None,
                                    this is a playground submission.
                                              """)
    timestamp   = models.DateTimeField("Timestamp",
                                       auto_now_add=True,
                                       help_text="""
                                       The time that the response was submitted.
                                                 """)
    code        = models.TextField("Code",
                                   help_text="""
                                   This is either the code of an autograded
                                   challenge or the URL of a jam.
                                             """)
    is_correct  = models.NullBooleanField("Is Correct",
                                          default=None,
                                          help_text="""
                                          When true, this challenge was correct.
                                          If None, the jam link hasn't been
                                          evaluated yet.
                                                    """)
    rom_size    = models.IntegerField("ROM size",
                                      default=0xffff,
                                      help_text="""
                                      The size of the compiled ROM of a successful
                                      response.
                                                """)
    runtime     = models.IntegerField("Running Time",
                                      default=0xffff,
                                      help_text="""
                                      The number of steps it takes to complete
                                      the test cases.
                                                """)
    
    # Representation of the challenge
    def __unicode__(self):
        return u"Challenge Response %d for %s" % (self.id,
                                                  self.challenge if self.challenge else "Playground")

