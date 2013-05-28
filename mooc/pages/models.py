# -*- coding: utf-8 -*-
from django.db import models

#from students.models import Student

# This object represents a page in the documentation.
class Page(models.Model):
    name    = models.SlugField("name",
                               unique=True, 
                               help_text="""The name of the page, used for
                               its URL.""")
    content = models.TextField("content",
                               help_text="""The text of the page, in
                               Markdown.""")
    
    # Unicode representation of the textbook page.
    def __unicode__(self):
        return u'%s'%(self.name)


