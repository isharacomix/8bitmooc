#! /bin/usr/env python

# Barry's super-lazy png2chr converter. Takes an PNG file and makes an NES
# pattern table (exactly $2000 bytes). It uses the RED of each pixel to decide
# the palette pixel to use.

# Usage: ./png2chr.py <png> <chr>

# Using Pygame...
import pygame
import sys

chrfile = sys.argv[2]
pngfile = sys.argv[1]

# Generate the surface we'll be using.
pygame.init()
surf = pygame.Surface( (128*2,128) )
surf.fill((255,255,255))
surf.blit( pygame.image.load( pngfile ), (0,0) )
spr = pygame.Surface( (8,8) )

chrdata = ""

# Returns 0 to 3 based on the color.
def bitval( col ):
    if col[0] > 200: return 0
    if col[0] > 120: return 1
    if col[0] > 45: return 2
    return 3

# The 'z' refers to the sprite vs the background pattern table.
for z in [0,1]:
    for y in range(16):
        for x in range(16):
            spr.blit( surf, (0,0), ((x*8+128*z,y*8),(8,8)) )
            
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
                    pix[a][b] = bitval(spr.get_at( (a,b) ))
            
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
                
                hi = "%c"%hb + hi
                lo = "%c"%lb + lo
            
            chrdata += lo + hi
    
f = open(chrfile,"wb")
f.write( chrdata )
f.close()

