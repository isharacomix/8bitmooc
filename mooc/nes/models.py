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


# Whenever the compile button is pressed, their code is saved in the DB in the
# form of a CodeSubmission record. This requires a circular reference to the
# Challenge model since challenges map back to the CodeSubmissions anyway.
class CodeSubmission(models.Model):
    student     = models.ForeignKey(Student,
                                    verbose_name="Student",
                                    null=True,
                                    blank=True,
                                    help_text="""The author of the challenge
                                    response.""")
    challenge = None
    #challenge   = models.ForeignKey("challenge.Challenge",
    #                                verbose_name="Challenge",
    #                                null=True,
    #                                blank=True,
    #                                help_text="""The challenge being responded
    #                                to. If None, this is a playground
    #                                submission.""")
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

