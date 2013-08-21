The Picture Processing Unit
===========================
The PPU (Picture Processing Unit) is responsible for all of the graphics
routines of the NES. The PPU provides eight memory-mapped registers that allow
the programmer to 


Registers
---------
### PPUCTRL ($2000)

This register sets most of the switches needed for rendering graphics on the
NES. This identifies which nametables and pattern tables are used for rendering
(discussed in the memory map section at the bottom of this page)

    76543210
    | ||||||
    | ||||++- Background nametable address
    | ||||    (0 = $2000; 1 = $2400; 2 = $2800; 3 = $2C00)
    | |||+--- VRAM address increment per CPU read/write of PPUDATA
    | |||     (0: add 1, going across; 1: add 32, going down)
    | ||+---- Sprite pattern table address for 8x8 sprites
    | ||      (0: $0000; 1: $1000; ignored in 8x16 mode)
    | |+----- Background pattern table address (0: $0000; 1: $1000)
    | +------ Sprite size (0: 8x8; 1: 8x16)
    +-------- Turn off/on (0/1) non-maskable interrrupts at vblank

Usually you write the values #%10010000 to this register when you're ready to
start the graphics, and write #%00000000 to turn off rendering when doing
complicated calculations.


### PPUMASK ($2001)

The PPU mask register contains several one bit switches to turn on and off
various graphical features such as monochrome displays, intensified colors, and
backgrounds. When any of the bits are set to 1, they are turned on.

    76543210
    ||||||||
    |||||||+- Set the screen to a monochrome display
    ||||||+-- Show background in leftmost 8 pixels of screen
    |||||+--- Show sprites in leftmost 8 pixels of screen
    ||||+---- Show background
    |||+----- Show sprites
    ||+------ Intensify reds
    |+------- Intensify greens
    +-------- Intensify blues

It may seem strange to have a separate flag for showing sprites and backgrounds
in the leftmost 8 pixels, but the reason for this is to provide a mechanic for
doing fancy scrolling effects. This is much more advanced than anything we will
be doing - usually the value that will be written to this register is #%00011110.


### PPUSTATUS ($2002)

The PPU status register is a read-only register that has three bits (5, 6, 7)
that provide information about the state of rendering.

    76543210
    |||
    ||+------ Sprite overflow. The intent was for this flag to be set
    ||        whenever more than eight sprites appear on a scanline, but a
    ||        hardware bug causes the actual behavior to be more complicated
    ||        and generate false positives as well as false negatives.
    |+------- Sprite 0 hit: equals to 1 when a nonzero pixel of sprite 0 overlaps
    |         a nonzero background pixel.
    +-------- Equals 1 when vertical blank has started, and resets to 0 after
              reading $2002.

This is often used with the BIT opcode, as it will set the sign and overflow
flags to bits 7 and 6 allowing a branch to be taken when there is a sprite 0
hit or a vertical blank occurs.

Bit 7 is set to 1 whenever the screen finishes rendering. Once the screen finishes
rendering, this is the optimal time to start doing anything related to graphics,
since you have the most time before the screen starts rendering again. This is
also the time at which an NMI begins, assuming bit 7 of PPUCTRL is set. This is
the flag that is read when waiting for the PPU to [[warmup]].

Reading this register also resets the latch used for PPUSCROLL and PPUADDR below.


### OAMADDR ($2003)

This register is used to set the pointer to the PPU's [[OAM]] buffer. OAM stands
for Object Access Memory, and contains the data used to render sprites on the
screen. A sprite is an 8x8 (or 8x16, depending on PPUCTRL's value) pixel tile
that can be rendered relatively quickly on the screen. The NES is capable of
rendering 64 sprites, with up to 8 sprites possible in any given scanline.

There are 256 bytes in this buffer, so writing any byte to this register will
set the pointer to point to one of those bytes. To change data after setting this
pointer, use OAMDATA. However, there is evidence that using this register actually
corrupts OAM data, making this an unreliable way to edit graphics data. In
practice, the only time this register should be written to is by writing a #0
to it before using OAMDMA (see the docs on [[OAM]]).


### OAMDATA ($2004)

When data is written to OAMDATA, the value is stored into the OAM buffer at
the location pointed to by OAMADDR. When a value is stored here, the value in
OAMADDR is incremented, so it is possible to store data in the entire buffer by
writing to this register 256 times.

In theory, it should be possible to read from this register as well, but this
is actually quite difficult to do since, during rendering, the values returned
from this address are rather unreliable. In fact, because writes to OAMADDR
(needed to change the address) are buggy anyway, this turns out to be extremely
impractical.


### PPUSCROLL ($2005)

The PPU scroll register is used to scroll the background horizontally and
vertically. The first time that this register is written to, the X position of
the scroll is set. The second and subsequent times, the Y position is set. To
reset the latch and enable the X position again, reading from PPUSTATUS starts
this over. Because the screen is wider than it is tall, legal X values range from
0 to 255, but Y values from 239 to 255 have glitchy behavior and should be
avoided. Writes to PPU scroll do not take effect until the next frame.

The PPU usually has enough memory to store two full backgrounds in its nametables.
When scrolling, the "primary" background is drawn using the nametable specified
in bits 0 and 1 of PPUCTRL, while the background being "scrolled to" is wrapped
around based on how the cartridge wires the memory map. This is discussed in
detail in the VRAM section below.


### PPUADDR ($2006)

Much like OAMADDR is the pointer to the 256 byte OAM buffer, PPUADDR provides a
pointer for access to the PPU's VRAM. Much like PPUSCROLL, writing to this
address is latched. The first write to this address sets the high byte of the
pointer, and the second and subsequent writes set the low byte. The VRAM
memory map is explained in detail in the VRAM section below.

Note that writes to PPUADDR also affect scrolling, so after using PPUADDR to
manipulate VRAM, be sure to read from PPUSTATUS to reset the latch and then set
PPUSCROLL to the desired location (usually 0,0 when you are just getting started).


### PPUDATA ($2007)

Much like OAMDATA, writing to PPUDATA sets the value pointed to by PPUADDR to
the stored value if the address is writabale (not read-only). After writing to
PPUDATA, PPUADDR is incremented by either 1 (if bit 2 of PPUCTRL is False) or 32
(if bit 2 of PPUCTRL is True).

Writing to PPUDATA is necessary to update the background nametables and the
color palettes. However, since using this register changes PPUADDR, it should
not be used except except when rendering is turned off using PPUMASK.


VRAM Memory Map
---------------
In addition to the [[CPU]] memory map, the PPU has its own internal memory called
VRAM. This contains three major collections of data: pattern tables, name tables,
and palettes. The pattern tables are basically the pixel data that makes up the
tiles used to render sprites and backgrounds, while name tables are tiles of 8x8
sprites that are assembled into a background. Palettes are simply the colors
assigned to the pixel values.

    $0000-$0FFF     Pattern Table #0
    $1000-$1FFF     Pattern Table #1
    $2000-$23BF     Name Table #0
    $23C0-$23FF     Attribute Table #0
    $2400-$27BF     Name Table #1
    $27C0-$27FF     Attribute Table #1
    $2800-$2BBF     Name Table #2
    $2BC0-$2BFF     Attribute Table #2
    $2C00-$2FBF     Name Table #3
    $2FC0-$2FFF     Attribute Table #3
    $3000-$3EFF     (mirror)
    $3F00-$3F0F     Background palette
    $3F10-$3F1F     Sprite palette
    $3F20-$00E0     (mirror)


### Pattern Tables

Pattern tables are essentially the sprite sheets of the NES. These contain the
pixel data for the tiles that are used to make up the sprites and backgrounds.
There are two $1000-byte pattern tables, which can hold 256 sprites each.
Normally one table is used for the Sprites, and the other is used for
Backgrounds, based on the values of bits 3 and 4 of PPUCTRL.

The NES supports 2-bit indexed sprites, meaning that each pixel of a tile can
be one of four colors (where color 0 is "transparency"). Tiles are 8x8 pixels,
so this means that each tile needs 128 bits (16 bytes) to be defined fully.
The Pattern tables is where these tiles are defined.

Tiles are drawn in a data format called a "bit plane" where the pixels for 
tile 'xx' are defined one row at a time where each of the 8 bits of a byte
correspond to a column of pixels in the rendered tile.

    Bit Planes                Pixel Pattern
    $0xx0=$41  01000001
    $0xx1=$C2  11000010
    $0xx2=$44  01000100
    $0xx3=$48  01001000
    $0xx4=$10  00010000
    $0xx5=$20  00100000         .1.....3
    $0xx6=$40  01000000         11....3.
    $0xx7=$80  10000000  =====  .1...3..
                                .1..3...
    $0xx8=$01  00000001  =====  ...3.22.
    $0xx9=$02  00000010         ..3....2
    $0xxA=$04  00000100         .3....2.
    $0xxB=$08  00001000         3....222
    $0xxC=$16  00010110
    $0xxD=$21  00100001
    $0xxE=$42  01000010
    $0xxF=$87  10000111         (transparent pixels represented by '.')

By layering these bit planes, a 2-bit sprite can be fully represented.

The interesting thing about the pattern tables is that they are not located on
the NES, but rather in the game cart itself, usually in the form of ROM. However,
some games store their patterns in RAM, making it possible to edit the sprite
sheets dynamically as the game ran.


### Name Tables

Name tables are data structures used to represent the background of the playfield.
Unlike sprites, which move around often and aren't fixed to a grid, the background
is a rigid grid of 8x8 tiles that are changed fairly infrequently using PPUADDR
and PPUDATA. There are two nametables located in the NES, but their memory
locations are different depending on how the game cartridge is wired.

         (0,0)     (256,0)     (511,0)
           +-----------+-----------+
           |           |           |
           |           |           |
           |   $2000   |   $2400   |
           |           |           |
           |           |           |
    (0,240)+-----------+-----------+(511,240)
           |           |           |
           |           |           |
           |   $2800   |   $2C00   |
           |           |           |
           |           |           |
           +-----------+-----------+
         (0,479)   (256,479)   (511,479)

In cartridges where scrolling is primarily horizontal, $2000/$2800 are the
memory locations of the first nametable and $2400/$2C00 are the locations of the
second. In games where it is primarily vertical, $2000/$2400 are the first and
$2800/$2C00 are the second. When using PPUSCROLL to scroll, this is how it knows
which nametable to get the next tiles from. In #8bitmooc, the emulator actually
gives you four nametables, allowing you to use both horizontal and vertical
scrolling. This means that two nametables would be located on the NES and two
would be located on the cartridge.

Nametables have 30 rows of 32 tiles each. Each tile requires one byte (meaning
that 60 pages are available on each nametable), and corresponds to the index of
the tile in the pattern table being used for the background. The remaining 64
bytes (4 pages) are used for the attribute table, which defines which of the
background palettes should be used for each tile. Each byte is assigned to a
4-block quad of tiles where the first two bits define the 2-bit color palette
for the top left tile, the second two bits define the top-right, the third two
define the bottom-left, and the last two define the bottom-right.

         ,-------+-------+-------+-------+-------+-------+-------+-------.
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xC0:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xC8:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xD0:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xD8:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xE0:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xE8:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
    2xF0:| - + - | - + - | - + - | - + - | - + - | - + - | - + - | - + - |
         |   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         +-------+-------+-------+-------+-------+-------+-------+-------+
    2xF8:|   .   |   .   |   .   |   .   |   .   |   .   |   .   |   .   |
         `-------+-------+-------+-------+-------+-------+-------+-------'


### Palettes



Special Thanks
--------------
Thanks to the folks behind the [NESDev Wiki

