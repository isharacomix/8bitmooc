from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from assembler.models import Pattern
import png

import os


# This reads our bitvalue from the colorization level of red.
def bitval( col ):
    if col[0] > 200: return 0
    if col[0] > 120: return 1
    if col[0] > 45: return 2
    return 3
def get_at( pix, x, y, d=3 ):
    pixelrow = pix[y]
    return pix[y][ x*d : x*d+3 ]


# This command parses PNG files and turns them into appropriate CHR sprite
# sheets that can be used by programmers.
class Command(BaseCommand):
    args = '<textbook directory>'
    help = 'Adds/updates worlds, lessons, challenges, and achievements '
    
    # Handler for 'create_world'
    def handle(self, *args, **options):
        if len(args) < 1:
            self.stderr.write('Please provide a directory containing the files '+
                              'relative to PROJECT_DIR.')
        
        sprites_dir = os.path.join(settings.PROJECT_DIR, '..', args[0])
        
        # Now load up all of the achievements.
        sprite_listing = os.listdir( sprites_dir )
        for slug in sprite_listing:
            try:
                img = png.Reader( os.path.join( sprites_dir, slug )  ).asDirect()
                pixels = []
                for p in img[2]:
                    pixels.append(p)
                d = img[3]["planes"]
                
                # Now try to make an achievement or get one already there.
                try: p = Pattern.objects.get(name=slug.split('.')[0])
                except: p = Pattern(name=slug.split('.')[0])
                
                p.code = ""
                for z in [0,1]:
                    for y in range(16):
                        for x in range(16):                            
                            pix = [[0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0],
                                   [0,0,0,0,0,0,0,0]]
                                   
                            for a in range(8):
                                for b in range(8):
                                    pix[a][b] = bitval( get_at( pixels, a+(x*8+128*z) ,b+(y*8), d ))
                                    
                            
                            hi = ""
                            lo = ""
                                   
                            for i in range(8):  # which row (byte in hi or lo)
                                lb = 0
                                hb = 0
                                for b in range(8): # which column (bit in hi[i])
                                    lb = lb << 1
                                    hb = hb << 1
                                    
                                    lb += 1 if pix[b][7-i] % 2 else 0
                                    hb += 1 if pix[b][7-i] > 1 else 0
                                
                                hi = ("%02X"%hb)[:] + hi
                                lo = ("%02X"%lb)[:] + lo
                            
                            p.code += lo + hi
                p.save()
                
                self.stdout.write('Wrote pattern: %s\n'%slug)
                
            except: self.stderr.write('Skipped pattern: %s\n'%slug)
        
        self.stdout.write('Successfully compiled spritesheets\n')
        
        
