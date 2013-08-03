# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import exceptions

from nes.models import Pattern, CodeSubmission
from students.models import Student


# Challenges are automatically graded assignments that give students a coding
# requirement and then check their code. If the "autograde" field is "None", then
# the challenges are graded manually.
class Challenge(models.Model):
    name            = models.CharField("Challenge Name",
                                       unique=True,
                                       max_length=200,
                                       help_text="""Full name of the challenge.""")
    slug            = models.SlugField("Challenge Slug",
                                       unique=True,
                                       help_text="""Short name of the challenge. 
                                       Used in the URL.""")
    ordering        = models.IntegerField("Ordering",
                                          help_text="""Order in which challenges
                                          are displayed.""")
    description     = models.TextField("Description",
                                       help_text="""Markdown description of the
                                       challenge.""")
    autograde       = models.SlugField("Autograde Function",
                                       blank=True,
                                       help_text="""Specifies the function for
                                       the autograder if this is an autograded 
                                       challenge. If left blank, it will be
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

    # Representation of the challenge
    def __unicode__(self):
        return u"%s" % (self.name)
    
    # Order these by difficulty.
    class Meta:
        ordering = ['ordering']


    # This method returns all of the challenges so that the they can be displayed
    # to the student.
    # TODO: Add SOS to the mix.
    # TODO: Add "waiting for grade"
    @staticmethod
    def show_for(student):
        challenges = Challenge.objects.all()
        complete_set = student.challenge_set.all()
        report = []
        for c in challenges:
            complete = False
            my_size = 0xFFFF
            my_speed = 0xFFFF
            best_size = 0xFFFFFF
            best_speed = 0xFFFFFF
            if c in complete_set:
                complete = True
                if c.autograde:
                    records = CodeSubmission.objects.filter(challenge=c, is_correct=True).order_by('rom_size')
                    if len(records) > 0:
                        best_size = records[0].rom_size
                        records = records.order_by('runtime')
                        best_speed = records[0].runtime
                    records = records.filter(student=student).order_by('rom_size')
                    if len(records) > 0:
                        my_size = records[0].rom_size
                        records = records.order_by('runtime')
                        my_speed = records[0].runtime
            report.append(( c, complete, my_size, my_speed, best_size, best_speed ))
        return report

