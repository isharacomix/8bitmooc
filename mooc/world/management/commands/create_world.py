from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from world.models import World, Stage, Achievement
from world.models import QuizChallenge, QuizQuestion
from assembler.models import AssemblyChallenge
from wiki.models import Page

import os


# This command updates the textbook database with new textbook pages. It will
# create new pages and overwrite old ones.
# First it opens the file named "worlds" and identifies how many worlds it will
# need to create. Then it creates all of the achievements in the "achievements"
# folder. Finally, it goes through all of the worlds and creates the stages for
# them, linking to wiki pages (if it needs to) and challenges (either the
# functions for assembly challenges or the multiple choice questions).
class Command(BaseCommand):
    args = '<textbook directory>'
    help = 'Adds/updates worlds, lessons, challenges, and achievements '
    
    # Handler for 'create_world'
    def handle(self, *args, **options):
        if len(args) < 1:
            self.stderr.write('Please provide a directory containing the files '+
                              'relative to PROJECT_DIR.')
        
        base_dir = os.path.join(settings.PROJECT_DIR, '..', args[0])
        
        # First, parse the "worlds" file and create all of the World objects.
        # Each line beginning with a % seperates out a world.
        data = ""
        f = open(os.path.join(base_dir, "worlds"))
        data = f.read()
        f.close()
        
        # Collect all of the worlds - in order.
        worlds = {}
        current = None
        i = 1
        for l in data.splitlines():
            if l.startswith("% "):
                current = l[2:].strip()
                worlds[current] = {"description":"", "name":current, "ordering":i, "prereq":None}
                i += 1
            elif current and l.startswith("%% "):
                l = l[3:].strip()
                if l.startswith("name:"): worlds[current]["name"] = l[5:].strip()
                elif l.startswith("prereq:"): worlds[current]["prereq"] = l[7:].strip()
            elif current:
                worlds[current]["description"] += l+"\n"
        
        # Actually create the objects.
        prereqs = {}
        for slug in worlds:
            try: w = World.objects.get(shortname=slug)
            except: w = World(shortname=slug)
            
            w.name = worlds[slug]["name"]
            w.description = worlds[slug]["description"]
            w.ordering = worlds[slug]["ordering"]
            w.prereq = None
            w.save()
            if worlds[slug]["prereq"]: prereqs[worlds[slug]["prereq"]] = w
        
        self.stdout.write('Successfully compiled the worlds!\n')
        
        # Now load up all of the achievements.
        achievement_listing = os.listdir( os.path.join(base_dir, "achievements") )
        for slug in achievement_listing:
            try:
                data = ""
                f = open(os.path.join(base_dir, "achievements", slug))
                data = f.read()
                f.close()
                
                # Now try to make an achievement or get one already there.
                try: a = Achievement.objects.get(shortname=slug)
                except: a = Achievement(shortname=slug)
                
                a.description = ""
                for l in data.splitlines():
                    if l.startswith("%% "):
                        l = l[3:].strip()
                        if l.startswith("name:"): a.name = l[5:].strip()
                        elif l.startswith("hidden:"): a.hidden = True if l[7:].strip() else False
                        elif l.startswith("won_in:"): a.won_in = World.objects.get(shortname=l[7:].strip())
                        elif l.startswith("graphic:"): a.graphic = l[8:].strip()
                        elif l.startswith("ordering:"): a.ordering = int(l[9:].strip())
                    else: a.description += l+"\n"
                if slug in prereqs:
                    a.prereq_for.add(prereqs[slug])
                a.save()
                
                self.stdout.write('Wrote achievement: %s\n'%slug)
                
            except: self.stderr.write('Skipped achievement: %s\n'%slug)
        
        self.stdout.write('Successfully compiled achievements\n')
        
        
        # For each world, go through and load the stages. However, we have to
        # save all the stages before we can set the prereqs.
        prereqs = {}
        for w in World.objects.all():
            stage_listing = os.listdir( os.path.join(base_dir, "%s"%(w.shortname) ) )
            
            for slug in stage_listing:
                try:
                    data = ""
                    f = open(os.path.join(base_dir, "%s"%(w.shortname), slug))
                    data = f.read()
                    f.close()
                    
                    # Now try to make a stage or get one already there.
                    try: s = Stage.objects.get(world=w, shortname=slug)
                    except: s = Stage(world=w, shortname=slug)
                    
                    c = None
                    prereqs2 = []
                    for l in data.splitlines():
                        if c is None:
                            if l.startswith("%% "):
                                l = l[3:].strip()
                                if l.startswith("name:"): s.name = l[5:].strip()
                                elif l.startswith("hidden:"): s.hidden = True if l[7:].strip() else False
                                elif l.startswith("graphic:"): s.graphic = l[8:].strip()
                                elif l.startswith("ordering:"): s.ordering = int(l[9:].strip())
                                elif l.startswith("lesson:"): s.lesson = Page.objects.get(title=l[8:].strip())
                                elif l.startswith("achievement_prereqs:"): prereqs2 += l[20:].strip().split()
                                elif l.startswith("stage_prereqs:"):
                                    prereqs["%s/%s"%(w.shortname, s.shortname)] = l[14:].strip().split()
                        else:
                            pass
                    if c: c.save()
                    s.challenge = c
                    s.save()
                    
                    s.prereqs1.clear()
                    s.prereqs2.clear()
                    for p in prereqs2:
                        s.prereqs2.add( Achievement.objects.get(shortname=p) )
                    s.save()
                    
                    self.stdout.write('Wrote stage: %s-%s\n'%(w.shortname, slug))
                    
                except: self.stderr.write('Skipped stage: %s-%s\n'%(w.shortname, slug))
            
        self.stdout.write('Successfully compiled stages\n')
        
        
        # Now compile the stage prerequisites. What a mess.
        for p in prereqs:
            world, stage = p.split('/',2)
            s1 = Stage.objects.get( world=(World.objects.get(shortname=world)), shortname=stage )
            for q in prereqs[p]:
                w, s = q.split('/', 2)
                s2 = Stage.objects.get( world=(World.objects.get(shortname=w)), shortname=s )
                s1.prereqs1.add( s2 )
                s1.save()
        
        self.stdout.write('Successfully compiled stage prereqs\n')

