#! /bin/usr/env python

# Barry's super-lazy chr2png converter. Takes an NES chr file and makes a PNG
# out of it. The PNG will be grayscale.

# Usage: ./chr2png.py <chr> <png>

# Using Pygame...
import pygame
import sys

chrfile = sys.argv[1]
pngfile = sys.argv[2]

# Generate the surface we'll be using.
pygame.init()
surf = pygame.Surface( (128*2,128) )
surf.fill((255,0,0))

f = open(chrfile,"rb")
data = f.read()
f.close()


colors = [(255,255,255),(170,170,170),(85,85,85),(0,0,0)]
spr = pygame.Surface( (8,8) )

# The 'z' refers to the sprite vs the background pattern table.
for z in [0,1]:
    for y in range(16):
        for x in range(16):
            spr.fill((0,255,0))
            lo = data[:8]
            hi = data[8:16]
            data = data[16:]

            # 
            pix = [[0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0]]
            for i in range(8):  # which row (byte in hi or lo)
                for b in range(8): # which column (bit in hi[i])
                    lv = 1 if ord(lo[i]) & (1 << (7-b)) else 0
                    hv = 2 if ord(hi[i]) & (1 << (7-b)) else 0
                    pix[b][i] = lv + hv
            
            
            # Now finish up and save the sprite.
            for a in range(8):
                for b in range(8):
                    spr.set_at( (a,b), colors[ pix[a][b] ] )
            surf.blit( spr, (x*8+128*z,y*8) )
    
pygame.image.save( surf, pngfile )

