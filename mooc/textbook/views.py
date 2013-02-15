from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

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


# This retrieves the page from the PROJECT_DIR/textbook folder. Returns the
# text of the file if it exists, and None if there is no file. We also return
# None if the page name is not a valid slug (fail hard).
def fetch_page(page):
    if not re.match(r'^[a-z0-9-]+$', page):
        return None
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
    
    # If the page doesn't exist, we go to an "oops" page.
    if s is None:
        return render(request, "textbook/page.html",
                      {'content': NO_PAGE, 'title': 'MISSING-PAGE'},
                      status=404)
    else:
        return render(request, "textbook/page.html", {
            'content': s, 'title': page,
        })

    
# The megafile is an aggregation of all of the wiki pages into one searchable
# text. Basically it takes all of the newlines and replaces them with spaces
# so that each file is on one line of the megafile, making it easy to search.
# The first line is the timestamp of the file, and it is rebuilt when it is
# 24 hours old.
def get_megafile():
    current_time = int(time.time())
    try:
        report = ""
        f = open(os.path.join(settings.PROJECT_DIR, 'textbook', ".megafile"))
        report = f.read()
        f.close()
        old_time = int(report.split()[0])
        
        # Check to see if it's too old.
        if current_time - old_time > 100000:
            raise Exception
        return report
    except:
        # It's too old, didn't exist, corrupted, etc.
        # Let's start over and rebuild it.
        report = str(current_time)+"\n"
        
        # Iterate over all of the files, avoiding the megafile.
        listing = os.listdir(os.path.join(settings.PROJECT_DIR, 'textbook'))
        for slug in listing:
            if '.' not in slug:
                f = open(os.path.join(settings.PROJECT_DIR, 'textbook', slug))
                s = f.read().replace("\n"," ")
                f.close()
                report += slug +": " + s +"\n"
        
        f = open(os.path.join(settings.PROJECT_DIR, 'textbook', ".megafile"),"w")
        f.write(report)
        f.close()
        return report


# This function returns a list of tuples in the format (slug, digest). The
# page is responsible for handling that list. To do this, we compile all of
# our text files into a single, searchable file (to avoid file I/O).
def find_pages(request, query):
    # TODO log the search!
    
    # Search the megafile for lines that contain the query and create
    # a results dictionary.
    data = {}
    querylist = query.lower().split()
    for page in get_megafile().splitlines()[1:]:
        k,v = page.split(":",1)
        score = 0
        miss = len(querylist)
        for q in querylist:
            hi = v.lower().rfind(q)
            lo = v.lower().find(q)
            if hi == -1:
                miss -= 1
            else:
                score += hi-lo
        if miss > 0:
            data[k] = v, score
    
    # Go through the text and find a digest that will allow the user to
    # find relevant data.
    results = data
    
    return render(request, "textbook/results.html",
                          {'results': results, 'query': query })


