from django.db import models


# Textbook Pages are models that are loaded into the database from the textbook
# content folder in order to avoid thread safety issues with flatfiles.
class Page(models.Model):
    title       = models.SlugField("title", unique=True,
                            help_text="Page title.")
    content     = models.TextField("content",
                            help_text="Page content.")
    
    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.title)
    
