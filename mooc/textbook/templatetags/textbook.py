from __future__ import absolute_import
from django import template
from ..markup import render_markup

register = template.Library()

@register.filter
def wikitext(text):
    return render_markup(text)

