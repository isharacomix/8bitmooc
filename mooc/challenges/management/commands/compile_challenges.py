from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from challenges.models import Challenge
from nes.models import Pattern

import os


# This command goes through a folder and compiles challenges. The markdown is
# kind of like markdown + yaml, where variables are denoted with double %%,
# and sections are denoted by a single %.
class Command(BaseCommand):
    args = '<challenge directory>'
    help = 'Creates all of the challenges for the MOOC '
    
    # Handler for 'create_world'
    def handle(self, *args, **options):
        if len(args) < 1:
            self.stderr.write('Please provide a directory containing the files '+
                              'relative to PROJECT_DIR.')
        
        base_dir = os.path.join(settings.PROJECT_DIR, '..', args[0])
        
        # Go through all of the challenges and compile them. This will update
        # existing challenges and add new ones.
        for slug in os.listdir( os.path.join(base_dir) ):
            try:
                data = ""
                f = open(os.path.join(base_dir, slug))
                data = f.read()
                f.close()
                
                # If the challenge is already there, update it!
                try: c = Challenge.objects.get(slug=slug)
                except: c = Challenge(slug=slug)
                
                c.description = ""
                c.preamble = ""
                c.postamble = ""
                c.autograde = ""
                
                stage = "description"
                for l in data.splitlines():
                    if l.startswith("%% "):
                        l = l[3:].strip()
                        if l.startswith("name:"): c.name = l[5:].strip()
                        elif l.startswith("pattern:"): c.pattern = Pattern.objects.get(name=l[8:].strip())
                        elif l.startswith("autograde:"): c.autograde = l[10:].strip()
                        elif l.startswith("ordering:"): c.ordering = int(l[9:].strip())
                    elif l.startswith("% "):
                        stage = l[2:].strip()
                    elif stage == "description": c.description += l+"\n"
                    elif stage == "preamble": c.preamble += l+"\n"
                    elif stage == "postamble": c.postamble += l+"\n"
                c.save()
                self.stdout.write('Wrote challenge: %s\n'%(slug))
                
            except: self.stderr.write('Skipped challenge: %s\n'%(slug))
        
        self.stdout.write('Successfully compiled challenges!\n')
        
