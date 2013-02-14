from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

import os

# This retrieves the page from the PROJECT_DIR/textbook folder. Returns the
# text of the file if it exists, and None if there is no file.
def fetch_page(page):
    try:
        report = ""
        f = open(os.path.join(settings.PROJECT_DIR, 'textbook', page))
        report = f.read()
        f.close()
        return report
    except:
        return None


# This method simply passes the string to the appropriate template and renders
# it in wiki creole.
def view_page(request, page='index'):
    s = fetch_page(page)
    
    # TODO This should fail more beautifully by going to a "not-found" page.
    # Remember this is not a wiki proper, so we don't go to an edit page.
    if s is None:
        raise Http404()
    else:
        return HttpResponse(s)
    
    
