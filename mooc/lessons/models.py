from django.db import models

from textbook.models import Page


# Milestones are basically achievements for students to get.
class Milestone(models.Model):
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

    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.name)


# Modules are the "worlds" that contain lessons. A Module is unlocked when the
# correct Milestone is reached. Milestones are like achievements, but not as
# big as the final Badge that represents the course.
class Module(models.Model):
    name        = models.CharField("name", max_length=128,
                            help_text="Human-readable module name.")
    shortname   = models.CharField("shortname", max_length=8, unique=True,
                            help_text="Short world name, usually a number.")
    graphic     = models.SlugField("graphic",
                            help_text="Filename of the glyph in the Module "+
                                      "img directory.")
    prereq      = models.ForeignKey(Milestone, verbose_name="prereq",
                            blank=True, null=True,
                            help_text="Which prerequisite is needed to start "+
                                      "this module?")
    ordering    = models.IntegerField("ordering", blank=True,
                            help_text="Modules are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    
    # Unicode representation.
    def __unicode__(self):
        return u"Module %s (%s)" % (self.shortname, self.name)


# If Modules are the "worlds", then lessons are the "stages". The name of the
# lesson is formatted: "[world.shortname]-[lesson.shortname]: [lesson.name]"
# So it would be like "1-1: Intro to ASM".
# Lessons contain a wiki page (just a textbook page) and the challenge (which
# is an autograded MC Quiz or ASM assignment). One can be null and then all
# that's left is the other. A lesson is completed when its tutorial has been
# read and it's challenge has received a 100% score.
class Lesson(models.Model):
    name        = models.CharField("name", max_length=128,
                            help_text="Human-readable lesson name.")
    shortname   = models.CharField("shortname", max_length=8, unique=True,
                            help_text="Short lesson name, usually a number.")
    
    # These take care of the course-related elements of the lesson.
    tutorial    = models.ForeignKey(Page, verbose_name="tutorial", blank=True,
                            help_text="The wiki page with this lesson's tutorial.")
    #challenge   = models.CharField("challenge", max_length=64, blank=True,
    #                        help_text="The challenge for this lesson.")
    # Not sure how to do challenges yet.
    prereq      = models.ManyToManyField("Lesson", blank=True,
                            help_text="If any of the prereqs have been completed,"+
                                      " then the lesson is considered open.")
    module      = models.ForeignKey(Module, verbose_name="module",
                            help_text="Which module is this lesson in?")
    hidden      = models.BooleanField("hidden", default=False,
                        help_text="If this is set, then the student can only "+
                                  " see the lesson when they have the prereqs.")
    reward      = models.ForeignKey(Milestone, verbose_name="reward",
                            null=True, blank=True,
                            help_text="Which Milestone is awarded for completing "+
                                      "this lesson?")
    
    # These represent how the lesson appears on the World Map (location, glyph)
    xlocation   = models.IntegerField("X", help_text="X location on the map.")
    ylocation   = models.IntegerField("Y", help_text="Y location on the map.")
    graphic     = models.SlugField("graphic",
                            help_text="Filename of the glyph in the Lesson "+
                                      "img directory.")
    ordering    = models.IntegerField("ordering", blank=True,
                            help_text="Lessons are ordered from lowest to "+
                                      "to highest when displayed in lists.")
    
    def __unicode__(self):
        return u"Lesson %s-%s: %s" % (self.module.shortname, self.shortname, self.name)
    
