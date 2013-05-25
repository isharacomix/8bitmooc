# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

import markdown
import re

register = template.Library()

# This actually renders the markup.
def render_markup(text, mini):
    lines = text.split()
    
    # Pre processing. Get rid of all links because we don't trust users!
    if mini:
        text = re.sub(r"\[(?P<page>[\w-]+)\]\([\S]+\)","\g<page>",text)
    
    # Do the markdownification.
    text = re.sub(r"\[\[(?P<page>[\w-]+)\]\]","[\g<page>](/help/\g<page>)",text)
    text = markdown.markdown(text, safe_mode="escape")
    
    # Post processing. If we are not in minimode, then let's add youtube videos.
    if not mini:
        text = re.sub(r"\{\{yt:(?P<yt>[\w-]+)\}\}",
                      '<iframe width="560" height="315"'+
                      'src="http://www.youtube.com/embed/\g<yt>"'+
                      'frameborder="0" allowfullscreen></iframe>',text)

    # Tell Django it's safe to use this code.
    return mark_safe(text)


@register.filter
def markup(text):
    return render_markup(text, False)
    
@register.filter
def minimarkup(text):
    return render_markup(text, True)

