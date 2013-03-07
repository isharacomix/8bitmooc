# -*- coding: utf-8 -*-
from django.db import models

from django.contrib.auth.models import User
from wiki.models import Page
from students.models import Student


# There are a pile of models here.
# WORLD MODELS: Handle the structure of the system
#   Milestone
#   Lesson
#   BaseChallenge
# CHALLENGE MODELS
#   QuizChallenge (made up of QuizQuestions)
# RESPONSE MODELS
#   QuizChallengeResponse (made up of QuizAnswers)


# Achievements are small accomplishments for learning tasks. Badges are like
# really big achievements. Achievements are also the keys that unlock new
# worlds.
class Achievement(models.Model):
    name        = models.CharField("name", max_length=128,
                            help_text="Human-readable milestone name.")
    hidden      = models.BooleanField("hidden", default=False,
                        help_text="If this is set, then the student can only "+
                                  " see the milestone's requirements when they have it.")
    description = models.TextField("description",
                        help_text="The requirements for the milestone, in a "+
                                  "human-readable format.")
    graphic     = models.SlugField("graphic",
                            help_text="Filename of the glyph in the Milestone "+
                                      "img directory.")
    ordering    = models.IntegerField("ordering", blank=True,
                            help_text="Milestones are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    awarded_to  = models.ManyToManyField(Student, blank=True,
                            help_text="Who has obtained this achievement?")   

    class Meta:
        ordering = ('ordering',)

    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.name)


# Worlds are the "modules" that contain lessons. A Module is unlocked when the
# correct Milestone is reached. Milestones are like achievements, but not as
# big as the final Badge that represents the course.
class World(models.Model):
    name        = models.CharField("name", max_length=128,
                            help_text="Human-readable module name.")
    shortname   = models.SlugField("shortname", max_length=8, unique=True,
                            help_text="Short world name, usually a number.")
    graphic     = models.SlugField("graphic",
                            help_text="Filename of the glyph in the Module "+
                                      "img directory.")
    description = models.TextField("description",
                        help_text="A description of the world in a "+
                                  "human-readable format.")
    prereq      = models.ForeignKey(Achievement, verbose_name="prereq",
                            blank=True, null=True,
                            help_text="Which prerequisite is needed to start "+
                                      "this module?")
    ordering    = models.IntegerField("ordering", blank=True, null=True,
                            help_text="Modules are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    
    class Meta:
        ordering = ('ordering',)
    
    # Unicode representation.
    def __unicode__(self):
        return u"World %s (%s)" % (self.shortname, self.name)


# This is the abstract Challenge class. Different challenges handle things
# in different ways. In order to make the code decent, I've decided to allow
# hard-coding here, so the challenge types need to be manually added in your
# code.
class BaseChallenge(models.Model):
    shortname       = models.SlugField("shortname", unique=True,
                        help_text="Short name for the challenge")
    content         = models.TextField("content",
                        help_text="Challenge content, in wikicreole.")
    
    # Put all of your challenge types in here. It's ugly, but it works.
    def challenge_type(self):
        c  = "none"
        for t in ["quizchallenge", "assemblychallenge"]:
            if hasattr(self, t): c = t
        return c
    
    # Unicode baby!
    def __unicode__(self):
        return u"%s: %s"%(self.challenge_type(), self.shortname)


# If Modules are the "worlds", then lessons are the "stages". The name of the
# lesson is formatted: "[world.shortname]-[lesson.shortname]: [lesson.name]"
# So it would be like "1-1: Intro to ASM".
# Lessons contain a wiki page (just a textbook page) and the challenge (which
# is an autograded MC Quiz or ASM assignment). One can be null and then all
# that's left is the other. A lesson is completed when its tutorial has been
# read and it's challenge has received a 100% score.
class Stage(models.Model):
    name        = models.CharField("name", max_length=128,
                            help_text="Human-readable lesson name.")
    shortname   = models.SlugField("shortname", max_length=8,
                            help_text="Short lesson name, usually a number.")
    
    # These take care of the course-related elements of the lesson.
    lesson      = models.ForeignKey(Page, verbose_name="lesson", blank=True, null=True,
                            help_text="The wiki page with this lesson's lesson.")
    challenge   = models.ForeignKey(BaseChallenge, verbose_name="challenge", blank=True,
                            null=True, help_text="The challenge for this lesson.")
    prereqs     = models.ManyToManyField("Stage", blank=True,
                            help_text="If any of the prereqs have been completed,"+
                                      " then the lesson is considered open.")
    world       = models.ForeignKey(World, verbose_name="world",
                            help_text="Which module is this lesson in?")
    hidden      = models.BooleanField("hidden", default=False,
                        help_text="If this is set, then the student can only "+
                                  " see the lesson when they have the prereqs.")
    reward      = models.ForeignKey(Achievement, verbose_name="reward",
                            null=True, blank=True,
                            help_text="Which Achievement is awarded for completing "+
                                      "this lesson?")
    
    # These represent how the lesson appears on the World Map (location, glyph)
    xlocation   = models.IntegerField("X", help_text="X location on the map.")
    ylocation   = models.IntegerField("Y", help_text="Y location on the map.")
    graphic     = models.SlugField("graphic",
                            help_text="Filename of the glyph in the Lesson "+
                                      "img directory.")
    ordering    = models.IntegerField("ordering", blank=True, null=True,
                            help_text="Lessons are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    completed_by= models.ManyToManyField(Student, blank=True,
                            help_text="Who has completed this stage?")
    
    class Meta:
        ordering = ('ordering',)
    
    def __unicode__(self):
        return u"Stage %s-%s: %s" % (self.world.shortname, self.shortname, self.name)


# Questions for the QuizChallenge type. There are two forms of questions,
# radio buttons (where selecting any correct answer wins) and checkboxes
# (where selecting them all wins).
class QuizQuestion(models.Model):
    shortname   = models.SlugField("shortname",
                        help_text="Short codename for the question.")
    question    = models.TextField("question",
                        help_text="The question in wiki-creole format.")
    choiceA     = models.TextField("choice A" )
    choiceB     = models.TextField("choice B", blank=True)
    choiceC     = models.TextField("choice C", blank=True )
    choiceD     = models.TextField("choice D", blank=True )
    choiceE     = models.TextField("choice E", blank=True )
    random_ok   = models.BooleanField("random ok?", default=False,
                        help_text="If this is set, then the choices will be "+
                                  "randomized each time they are seen. Don't "+
                                  "check this if you have a 'none of the above' "+
                                  "or 'all of the above' choice?")
    multiple_ok = models.BooleanField("multiple ok?", default=False,
                        help_text="If this is set, then the choices will be "+
                                  "selected via a check box rather than a radio "+
                                  "button.")
    correctA    = models.BooleanField("A is correct", default=False )
    correctB    = models.BooleanField("B is correct", default=False )
    correctC    = models.BooleanField("C is correct", default=False )
    correctD    = models.BooleanField("D is correct", default=False )
    correctE    = models.BooleanField("E is correct", default=False )
    ordering    = models.IntegerField("ordering", blank=True, null=True,
                            help_text="Questions are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    
    class Meta:
        ordering = ('ordering',)
    
    def __unicode__(self):
        return u"%s: %s..." % (self.shortname, self.question[:64])


# Challenge type: Multiple Choice Quiz
class QuizChallenge(BaseChallenge):
    questions   = models.ManyToManyField(QuizQuestion, blank=True,
                        verbose_name="questions",
                        help_text="The questions for this quiz.")
    randomize   = models.BooleanField("random ok?", default=False,
                        help_text="If this is set, then the questions will be "+
                                  "randomized each time they are seen")
    score       = models.IntegerField("score",
                                      help_text="How many points is this worth?")


# An answer to a single quiz question.
class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, verbose_name="question")
    selectedA = models.BooleanField("A was selected", default=False )
    selectedB = models.BooleanField("B was selected", default=False )
    selectedC = models.BooleanField("C was selected", default=False )
    selectedD = models.BooleanField("D was selected", default=False )
    selectedE = models.BooleanField("E was selected", default=False )
    correct   = models.BooleanField("Answer was correct", default=False )
    
    def __unicode__(self):
        return u'QuizAnswer %d'%self.id


# The form submitted when a multiple-choice quiz is completed.
class QuizChallengeResponse(models.Model):
    challenge = models.ForeignKey(QuizChallenge, verbose_name="challenge")
    answers   = models.ManyToManyField(QuizAnswer, verbose_name="answers")
    student   = models.ForeignKey(Student, verbose_name="student")
    timestamp = models.DateTimeField("timestamp", auto_now=True)
    correct   = models.BooleanField("All answers correct", default=False )
    score     = models.IntegerField("correct answers")
    
    def __unicode__(self):
        return u'QuizResponse %d from %s'%(self.id,self.student.username)

