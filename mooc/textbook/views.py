from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404)
from django.shortcuts import render, redirect

import os
import time

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
        
        # Iterate over all of the files.
        # for f in files:
        #    s = f.read().replace("\n"," ")
        #    report += slug +": " + s +"\n"
        
        f = open(os.path.join(settings.PROJECT_DIR, 'textbook', ".megafile"),"w")
        f.write(report)
        f.close()
        return report
    

# This function returns a list of tuples in the format (slug, digest). The
# page is responsible for handling that list. To do this, we compile all of
# our text files into a single, searchable file (to avoid file I/O).
def find_pages(request, query):
    # TODO log the search!
    
    report = []
    
    # Search the megafile for lines that contain the query.
    data = get_megafile().split()[1:]
    
    return HttpResponse(str(report))


