from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from wiki.models import Page

import os


# This command updates the textbook database with new textbook pages. It will
# create new pages and overwrite old ones.
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
        
        # Iterate over all of the filenames.
        for slug in listing:
            try:
                data = ""
                f = open(os.path.join(textbook_dir, slug))
                data = f.read()
                f.close()
                
                # Now try to make a page Model.
                try: page = Page.objects.get(title=slug)
                except: page = Page(title=slug)
                page.content = data
                page.save()
                
                self.stdout.write('Wrote textbook page: %s\n'%slug)
                
            except: self.stderr.write('Skipped textbook page: %s\n'%slug)
        
        self.stdout.write('Successfully compiled textbook pages\n')
    

