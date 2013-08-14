NES Hardware
============
For the first half of this tutorial, you've been learning about assembly
language: the code you have to write in order to power the hardware. That's
only half of the story, of course, since now, you have to learn about the
hardware itself!

The NES hardware was designed to facilitate the development of video games,
offering a very natural interface between the assembly code, the graphics, the
sounds, and the controller.


Memory Mapped Registers
-----------------------
There are no opcodes related to the hardware of the NES. There isn't a
"draw_sprite" or "play_sound" instruction. Instead, all of the hardware is
powered by **memory-mapped** registers. What this means is that certain memory
addresses, such as $4017, instead of being hooked up to memory, are actually
connected to the hardware on the NES. You can control the hardware by writing
certain values to these addresses.


Picture Processing Unit
-----------------------
The [[PPU|ppu]] has 8 registers starting from address $2000. This is a high level
overview of the registers (check their specific pages for information on how
to use them.

 * ```$2000```: PPU Controller, write-only. Turns on graphics for the NES.
 * ```$2001```: PPU Mask, write-only. Makes it possible to turn on and off
   specific graphical elements.
 * ```$2002```: PPU Status, read-only. Allows you to check information about
   where the PPU is currently drawing information.
 * ```$2003```: [[OAM|oam]] Address, write-only. Sets the address in OAM to
   access.
 * ```$2004```: OAM Data, read/write. Not exactly reliable, but a way to read
   and write data from the address in OAM.
 * ```$2005```: Scroll, allows 2 writes. This allows you to scroll the background,
   used for many games. The first time you write to it, it scrolls horizontally.
   The second time, it scrolls vertically. After that, future writes have no
   effect - you have to read $2002 in order to start over.
 * ```$2006```: PPU Address, allows 2 writes. Sets the address of VRAM to write
   to. You have to write to VRAM in order to set up your backgrounds and your
   color palettes. The first write sets the high byte, and the second sets the
   low byte.
 * ```$2007```: PPU Data, read/write. This allows you to write to the address
   specified in $2006. After writing, the pointer will be incremented.

The registers for the PPU actually range from $2000-$3FFF, but these eight
registers are simply copied multiple times. In other words, writing to $2008 is
exactly the same as writing to $2000. In order to save money on developing the
NES, the extra memory was simply rewrapped around to the same hardware, and
programmers can take advantage of these features to make their programs harder
to disassemble.


Audio Processing Unit
---------------------
The [[APU|apu]] has 24 registers starting from address $4000 to $4017. Unlike
the PPU, there are no mirrored registers. All of the addresses from $4018 to
$FFFF are reserved for the game cartridge. The APU also has the hardware used
for the game controllers.

The APU has five sound channels to play music and sound effects. Each sound
channel has 4 memory addresses. The final four memory addresses are for
the controller and, oddly, a graphics operation.

 * ```$4000-$4003```: Square wave 1.
 * ```$4004-$4007```: Square wave 2.
 * ```$4008-$400B```: Triangle wave.
 * ```$400C-$400F```: Noise generator.
 * ```$4010-$4013```: DMC sampler.
 * ```$4014```: OAM DMA. Writing an address to this register is done to update
   the information related to sprites on the screen.
 * ```$4015```: Sound channel register. Turns on and off sound effects.
 * ```$4016```: Controller 1 (when read) and controller feedback (when written)
 * ```$4017```: Controller 2 (when read) and sound frame control (when written)


Making sense of the addresses
-----------------------------
If you try to write programs using these memory addresses, you'll likely go
insane. However, you can use the [[.define|define]] opcode to make things a bit
easier to write and read.

    .define PPUCTRL=$2000
    .define PPUMASK=$2001
    .define PPUSTAT=$2002
    ; ... and so on

This way, instead of trying to make sense of code like

    STA $2001
    
You can use

    STA PPUMASK
    
instead, which is much more readable. A list of definitions you can copy and
paste into your programs is available [[here|memory_map]].

