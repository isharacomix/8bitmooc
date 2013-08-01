from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pages.models import Page

import os


# This command updates the help database with new help pages. It will create
# new pages and overwrite old ones.
class Command(BaseCommand):
    args = '<textbook directory>'
    help = 'Adds/updates textbook pages '
    
    # Handler for 'write_textbook'
    def handle(self, *args, **options):
        if len(args) < 1:
            self.stderr.write('Please provide a directory containing the files '+
                              'relative to PROJECT_DIR.')
    
        textbook_dir = os.path.join(settings.PROJECT_DIR, '..', args[0])
        listing = os.listdir( textbook_dir )
        
        # Iterate over all of the folders.
        for folder in listing:
            page_listing = os.listdir( os.path.join(textbook_dir, folder) )
            for md in [f for f in page_listing if f.endswith(".md")]:
                try:
                    data = ""
                    f = open(os.path.join(textbook_dir, folder, md))
                    data = f.read()
                    slug = md[:-3]
                    f.close()
                    
                    # Now try to make a page Model.
                    try: page = Page.objects.get(name=slug)
                    except: page = Page(name=slug)
                    page.content = data
                    page.save()
                    
                    self.stdout.write('Wrote textbook page: %s\n'%md)
                    
                except: self.stderr.write('Skipped textbook page: %s\n'%md)
        
        self.stdout.write('Successfully compiled textbook pages\n')
    


