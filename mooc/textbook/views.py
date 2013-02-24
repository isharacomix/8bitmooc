from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

from textbook.models import Page

import os
import time
import re


# Error text when reaching a page that doesn't exist.
NO_PAGE = """
= Oops! That page does not exist!

You've reached a page in error - it was probably a typo
by one of our editors.

Please either hit the back button or return to the [[index|front page]].
"""


# This method simply passes the string to the appropriate template and renders
# it in wiki creole.
def view_page(request, page=None):
    if page is None: return redirect( "textbook_page", page="index" )
    try:
        p = Page.objects.get(title=page)
        return render(request, "textbook_page.html", {
                               'content': p.content, 'title': p.title
                               })
    except exceptions.ObjectDoesNotExist:
        return render(request, "textbook_page.html",
                      {'content': NO_PAGE, 'title': 'MISSING-PAGE'},
                      status=404)

    
# This function returns a list of tuples in the format (slug, digest). The
# page is responsible for handling that list.
def find_pages(request, query):
    # TODO log the search!
    
    # Go through the text and find a digest that will allow the user to
    # find relevant data.
    data = {}
    results = data
    
    return render(request, "textbook_search.html",
                          {'results': results, 'query': query })


