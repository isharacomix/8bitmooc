# -*- coding: utf-8 -*-
from django.db import models

from students.models import Student

# The Pattern table stores binary data for the purposes of Sprite Sheets.
# Patterns are selected from a drop down box when included in projects.
# The data is actually stored in ASCII Hex (maybe upgrade to ASCII85 in the
# future).
class Pattern(models.Model):
    name = models.SlugField("name",
                            unique=True, 
                            help_text="""The name of the pattern, used for its
                            URL.""")
    code = models.TextField("code",
                            help_text="""The binary data for the pattern encoded
                            in ASCII hex. It makes the data larger than it would
                            be in the actual binary, but makes it portable
                            too.""")
    
    # Unicode representation of the pattern.
    def __unicode__(self):
        return u'Pattern %s'%(self.name)


# Students are able to publish games so that people can play them in the
# arcade. Source code is more often than not smaller than the actual game,
# so we'll use source code as the storage format.
class Game(models.Model):
    title   = models.CharField("title",
                               max_length=200,
                               help_text="""The game title.""")
    code    = models.TextField("code",
                               help_text="""Game source code.""")
    description = models.TextField("Description",
                                   help_text="""Description of the game in
                                   minimarkdown.""")
    pattern = models.ForeignKey(Pattern,
                                verbose_name="Pattern",
                                null=True,
                                blank=True,
                                help_text="""Spritesheet for the game.""")
    hits    = models.IntegerField("hits",
                                  default=0,
                                  help_text="""Number of visits to the game.""")
    authors = models.ManyToManyField(Student,
                                     blank=True,
                                     help_text="""The authors of this project.
                                     Displayed, linked to their twitter accounts
                                     if available.""")

    # Unicode representation of the pattern.
    def __unicode__(self):
        return u'Game %d'%(self.id)

