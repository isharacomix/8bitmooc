Object Attribute Memory
=======================
OAM is an internal buffer in the PPU used to store information for sprites.
The OAM buffer is 256 bytes wide, and each sprite requires 4 bytes of data to
be rendered, meaning that the buffer can contain 64 sprites at a time. The
programmer can not write directly to the OAM buffer, but can use registers on
the [[PPU]] and [[APU]] to alter these values.


Format
------
### Byte 0: Y position
The first byte contains the vertical position of the top-left pixel of the
sprite where lower values mean closer to the top. Sprites do not wrap around the
screen when they reach the edge, meaning that it's possible to effectively hide
a sprite by storing a value greater than 239 as its Y position.

Sprites do not wrap around the screen, so the only legal values are 0
(top of the screen) through 238 (bottom of the screen). Any other value makes
the sprite invisible (since it's below the bottom of the screen).


### Byte 1: Pattern Index
This byte indicates which tile from the pattern table will be rendered
for this sprite. How this works depends on the value of bit 5 of PPUCTRL. If
this bit is False, the sprite is 8x8 pixels, and if the bit is True, sprites
will be 8x16 pixels.

For 8x8 pixel sprites, the value in OAM Byte 1 indicates which of the 256 tiles
in the pattern table will be rendered. The pattern table that is used is based
on the value in bit 3 of PPUCTRL.

For 8x16 pixel sprites, bit 3 of PPUCTRL is ignored, and the table to be used is
instead indicated by bit 0 of OAM Byte 1. The other 7 bits indicate the tile
number for the *top* of the sprite, while the bottom of the sprite is simply the
tile immediately to the right.

    abcdefghijklmnop        In this example, let's say we are using 8x16
    qrstuvwxyz,.?!@#        sprites and the value passed into OAM Byte 1 is
    abcdefghijklmnop        %00000110.
    qrstuvwxyz,.?!@#        
    abcdefghijklmnop        The tile selected in this case will be sprite 6,
    qrstuvwxyz,.?!@#        which is 'g'. The bottom will be the tile that
    abcdefghijklmnop        is directly to the right, so sprite 6 is rendered
    qrstuvwxyz,.?!@#        on the screen as
    abcdefghijklmnop
    qrstuvwxyz,.?!@#            g
    abcdefghijklmnop            h
    qrstuvwxyz,.?!@#
    abcdefghijklmnop        If we increment bits 1 through 7, %00001000, the
    qrstuvwxyz,.?!@#        next tiles would be used: 'i' and 'j'
    abcdefghijklmnop
    qrstuvwxyz,.?!@#

For more information, read the [[PPU]] entries about pattern tables.


### Byte 2: Properties
This byte contains other properties about the sprite.

    76543210
    |||   ||
    |||   ++- Palette (4 to 7) of sprite (VRAM location $3F10 to $3F1F)
    ||+------ Priority (0: in front of background; 1: behind background)
    |+------- Flip sprite horizontally
    +-------- Flip sprite vertically


### Byte 3: X position
The final byte contains the horizontal position of the top-left pixel of the
sprite where lower values mean closer to the left. Just as with the Y position,
sprites do not wrap when they run off the side of the screen.


Altering OAM Data
-----------------
The best way to alter OAM is by using Direct Memory Access, or DMA. To do this,
simply section off one page of RAM, such as Page 3, and store the information for
all of your sprites in the page as if it were OAM. After everything is set up,
write a zero to OAMADDR in order to point the OAM to the beginning of the buffer,
and then write the value of your page (such as #3) to register $4014 (OAMDMA).
This will copy the entire page from RAM into the buffer.

In theory, it should be possible to edit OAM data one byte at a time by setting
OAMADDR and then writing to OAMDATA, there is evidence that suggests that
writes to OAMADDR actually corrupt data in the OAM buffer, which makes this an
unreliable way of setting data that some emulators either fail to emulate
correctly or fail all out. It is suggested that you use DMA for all coding
related to sprites.

