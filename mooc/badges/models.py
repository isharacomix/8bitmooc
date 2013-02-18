from django.db import models
from django.contrib.auth.models import User


# Badges are major achievements that implement the Mozilla Open Badges API.
# Unlike milestones, which are internal achievements, Badges can be taken out
# of the site and flaunted in their badge backpacks.
class Badge(models.Model):
    name        = models.CharField("name", max_length=128,
                        help_text="Human-readable badge name.")
    shortname   = models.SlugField("shortname", unique=True,
                        help_text="Badge shortname - used in the URL.")
    shortdesc   = models.CharField("short description", max_length=128,
                        help_text="Brief badge description.")
    description = models.TextField("description",
                        help_text="The full badge description, in a human-readable, "+
                                  "wiki-creole format.")
    graphic     = models.SlugField("graphic",
                        help_text="Filename of the glyph in the Badge "+
                                  "img directory.")
    ordering    = models.IntegerField("ordering", blank=True,
                        help_text="Badges are ordered from lowest to "+
                                  "to highest when displayed in lists.")
    awarded_to  = models.ManyToManyField(User, blank=True,
                            help_text="Who has this badge? This relation has "+
                                      "to be set out-of-band.")

    # Unicode representation.
    def __unicode__(self):
        return u"%s" % (self.name)

    # Returns True if the specified user has this badge.
    def held_by(self, user):
        return user in self.awarded_to.all()

