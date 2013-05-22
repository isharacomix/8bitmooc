# -*- coding: utf-8 -*-
from django.db import models

#from students.models import Student

# The Pattern table stores binary data for the purposes of Sprite Sheets.
# Patterns are selected from a drop down box when included in projects.
# The data is actually stored in ASCII Hex (maybe upgrade to ASCII85 in the
# future).
class Pattern(models.Model):
    name = models.SlugField("name",
                            unique=True, 
                            help_text="""
                            The name of the pattern, used for its URL.
                                      """)
    code = models.TextField("code",
                            help_text="""
                            The binary data for the pattern encoded in ASCII
                            hex. It makes the data larger than it would be in
                            the actual binary, but makes it portable too.
                                      """)
    
    # Unicode representation of the pattern.
    def __unicode__(self):
        return u'Pattern %s'%(self.name)


