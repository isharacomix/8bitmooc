The NES Memory Map
==================
The 16-bit address bus of the 6502 is capable of accessing $10000 possible
addresses from $0000 to $FFFF. However, rather than directly connecting memory
to these lines, many of these memory addresses are used to access the registers
exposed by the other hardware on the NES, such as the [[PPU]] and the [[APU]].
The basic division of the memory map is as follows:

    $0000-$00FF     The Zero Page (RAM)
    $0100-$01FF     The Stack (RAM)
    $0200-$07FF     General Purpose RAM
    $0800-$1FFF     Mirrored RAM
    $2000-$2007     PPU Registers
    $2008-$3FFF     Mirrors of PPU Registers
    $4000-$4017     APU Registers
    $4018-$7FFF     Game Cart Hardware
    $8000-$FFF9     PRG ROM
    $FFFA-$FFFF     Vector Table

Much of the memory addresses are "mirrored", which means that the there are
multiple different "addresses" that point to the same device. For example,
reading or writing memory address $09E0 has the exact same effect as reading
or writing $1E0, since the higher address is simply a mirror of the lower
address.

Also note that the [[PPU]]'s [[video ram|vram]] also has a memory map.


The Zero Page ($0000-$00FF)
---------------------------
Memory on the 6502 is divided into "pages", which are simply contiguous blocks
of 256 bytes of memory. The high byte of the address is "$00", so memory address
$0076 would be the $76th byte on the $00th page.

The zero page is a special location on RAM that is faster to access than other
RAM. Many operations, when given the zero page as the argument, are able to
do the operation in one less clock cycle and with one less byte in the resulting
image because the page number is implied to be zero. Because the 6502 has only
three registers, the zero page is often used as a scratch space for calculations
so that information can be quickly stored and moved around in complicated
computations.

The zero page is also used in *indirect addressing*, which is covered in the
section on the [[CPU]] and its [[opcodes]].


The Stack ($0100-$01FF)
-----------------------
The stack is another special part of RAM that exists on the $01 page. The stack
is a special data structure called a "last-in, first-out" data structure, that
operates something like a deck of cards. Whenever interrupts occur on the NES,
the current location in memory has to be stored somewhere so that when the
interrupt is over, the CPU can return to where it left off. The place where the
memory location is stored is the stack.

Data is transferred to and from the stack in operations called *pushes* and
*pulls*. Data is pushed to and pulled from the "top" of the stack, and the memory
location that counts as the "top" of the stack is stored in a special register
called the **stack pointer** (abbreviated **SP**). When data is pushed, the
memory location pointed to by SP is overwritten, and SP is decremented by 1
(in other words, the stack grows downward). When data is pulled, SP is
incremented by 1 and then the data at that memory location is read.

                 Push 5     Push 7      Pull        Push 6
    [00]* $1FF   [05]       [05]        [05]        [05]
    [00]  $1FE   [00]*      [07]        [07]*       [06]
    [00]  $1FD   [00]       [00]*       [00]        [00]
    [00]  $1FC   [00]       [00]        [00]        [00]
    [00]  $1FB   [00]       [00]        [00]        [00]

      SP=$1FF    $1FE       $1FD        $1FE        $1FD

The stack is fairly small, and it is up to the programmer to make sure that it
doesn't overflow, or else the program could end very badly. Also, while it is
possible to use the stack as general purpose RAM, this is highly dangerous,
since it's possible that an interrupt can occur at any time and corrupt any
data stored there, breaking your program.


General Purpose RAM ($0200-$07FF)
---------------------------------
Out of the 2 KB of RAM provided by the NES, 512 bytes are reserved for the zero
page and stack, leaving 1.5 KB for the programmer to use to manage variables in
the game such as character position, HP, Strength, and so on. If your game has
different modes, sometimes it is possible to use the same memory locations for
more than one variable, as long as both variables are not needed at the same
time. To name a memory location as a variable, use the ```.define``` opcode.
Giving memory locations descriptive names not only makes code more readable, it
also makes it possible to change the memory locations without having to update
every point in the code where it is used.

    .define player_hp=$200
    .define player_mp=$201
    .define player_x=$202
    .define player_y=$203

Normally, when using sprites, an additional full page of 256 bytes needs to be
reserved to keep track of sprite positions and properties - more on this topic
can be found in the page on the [[PPU]].


PPU Registers ($2000-$2007)
---------------------------
The Picture Processing Unit (or [[PPU]]) is the NES hardware responsible for
rendering graphics on the television screen. The PPU exposes 8 registers, which
are listed here and discussed in more detail on the PPU spec sheet.

    $2000   PPUCTRL     Used to turn on and off NMI generation on each frame
    $2001   PPUMASK     Used to turn on and off rendering of sprites/backgrounds
    $2002   PPUSTATUS   Can be read by the programmer to see when rendering occurs
    $2003   OAMADDR     Set the address for [[OAM]] (sprite locations and properties)
    $2004   OAMDATA     Modify OAM sprite locations or properties
    $2005   PPUSCROLL   Scrolls the background
    $2006   PPUADDR     Sets the VRAM memory pointer
    $2007   PPUDATA     Stores data in VRAM (for changing palettes or backgrounds)

The PPU has its own internal memory map for VRAM, which is discussed on the
PPU spec sheet.


APU Registers ($4000-$401F)
---------------------------
The Audio Processing Unit (or [[APU]]) is the NES hardware for sound processing,
but the memory address range is also shared with the circuitry used for controller
input and some routines useful for graphics processing. The NES provides five sound
channels: two square waves, a triangle wave, a noise generator, and DMC channel.
Unlike the rest of the hardware, none of the APU registers are mirrored. Once
again, they are briefly listed here, and discussed in deeper detail on the spec
sheet.

    $4000   SQ1VOL      Volume and duty cycle for square wave 1
    $4001   SQ1SWEEP    Sweep for square wave 1
    $4002   SQ1LO       Low byte of period (pitch) for square wave 1
    $4003   SQ1HI       High byte of period and counter for square wave 1
    $4004   SQ2VOL      Volume and duty cycle for square wave 2
    $4005   SQ2SWEEP    Sweep for square wave 2
    $4006   SQ2LO       Low byte of period (pitch) for square wave 2
    $4007   SQ2HI       High byte of period and counter for square wave 2
    $4008   TRILINEAR   Linear counter for triangle wave
    $4009   (n/a)
    $400A   TRILO       Low byte of period (pitch) for triangle wave
    $400B   TRIHI       High byte of period and counter for triangle wave
    $400C   NOISEVOL    Volume for noise generator
    $400D   (n/a)
    $400E   NOISEMODE   Pitch and shape of noise generator
    $400F   NOISELEN    Counter for the noise generator
    $4010   DMCFREQ     Play mode and frequency for DMC channel
    $4011   DMCRAW      7-bit DAC
    $4012   DMCSTART    Starting position of the DMC waveform
    $4013   DMCLEN      Length of the DMC waveform
    $4014   OAMDMA      Use this to copy a page of RAM into the OAM (sprite data)
    $4015   SNDCHAN     Enable/disable sound channels
    $4016   CONTROL1    Controller 1 status
    $4017   CONTROL2    (when read) Controller 2 status
    $4017   FRAMECTRL   (when written) Frame counter


Game Cart Hardware ($4018-$7FFF)
--------------------------------
Since hardware in the NES can simply have its registers mapped directly to CPU
memory addresses, in order to improve the number of features that games could
have, the same technique is available in carts. Since there are only $8000 bytes
left in ROM for games, many carts take advantage of a technique called
"bank switching" where they use special hardware in this memory range to replace
entire chunks of memory with entire other chunks. This allows games to be much
larger than they would be otherwise. Also, in order to make advanced games like
RPGs, some carts had battery-backed RAM built into the cartridge in order to
save data, usually mapped at the $6000 range.

In #8bitmooc, we will not be exploring this functionality, however the NES
development community has extensive documentation on the different types of
carts and how they differ in their usage of the hardware in this memory range.


PRG ROM ($8000-$FFF9)
---------------------
PRG ROM (Program Read-Only Memory) is where the game code goes. All of the code
for the game must fit in this space. ROM is divided into 16 KB chunks called
"banks" (hence the term "bank switching"). As its name implies, it may be read
from, but may not be written to. When you assemble an NES game, this is why what
you produce is called a "ROM".

Another type of ROM is CHR ROM, which is discussed in the section on the [[PPU]].


Vector Table ($FFFA-$FFFF)
--------------------------
The last six bytes of ROM are the vectors that show where the program begins.
When the 6502 starts, it looks at the memory address located in $FFFC and starts
the program at that location. This is usually a label to a location in ROM.
These addresses are stored in the usual little-endian format, where the byte 
number is listed first, followed by the page number.

    Lo Byte     Hi Byte     Vector
    $FFFA       $FFFB       NMI
    $FFFC       $FFFD       RESET
    $FFFE       $FFFF       BRK/IRQ

The RESET vector is jumped to whenever the power is cycled either by powering up
or having the reset button pressed. The reset button doesn't necessarily clean
up the data in memory, so it is important that your reset routine clears memory
for you.

The NMI vector is jumped to every time the screen refreshes. This means that you
can put code in here that you don't want to proceed in extremely fast loops, like
user input and enemy movement.

The IRQ/BRK vector is jumped to whenever a BRK instruction is read, or whenever
and IRQ is sent by the system, usually as a result of setting the Frame Counter
(see the [[APU]]). However, if the Interrupt flag is set, then IRQs are ignored.

In code, these locations are usually defined in the following way:

    START:
        ; some code goes here
        
    NMI:
        ; some more code goes here
    
    IRQ:
        ; even more code goes here
    
    .org $FFFA
    .dw NMI
    .dw START
    .dw IRQ

This code takes the labels of the program and then places their values directly
in ROM at the specified locations. You can see this in action in the [[warmup]]
code.
    

Putting the memory map in code
------------------------------
If you want to be able to refer to memory locations by their names and not their
hex numbers, simply include the following code snippet in your programs. This
is already a part of the [[warmup]] code.

    ;----------------------------------------
    ; Define all of the memory locations in the memory map.
    ;----------------------------------------
        .define ZEROPAGE=$0000              ;
        .define STACK=$0100                 ;
        .define PPUCTRL=$2000               ;
        .define PPUMASK=$2001               ;
        .define PPUSTATUS=$2002             ;
        .define OAMADDR=$2003               ;
        .define OAMDATA=$2004               ;
        .define PPUSCROLL=$2005             ;
        .define PPUADDR=$2006               ;
        .define PPUDATA=$2007               ;
        .define SQ1VOL=$4000                ;
        .define SQ1SWEEP=$4001              ;
        .define SQ1LO=$4002                 ;
        .define SQ1HI=$4003                 ;
        .define SQ2VOL=$4004                ;
        .define SQ2SWEEP=$4005              ;
        .define SQ2LO=$4006                 ;
        .define SQ2HI=$4007                 ;
        .define TRILIN=$4008                ;
        .define TRILO=$400A                 ;
        .define TRIHI=$400B                 ;
        .define NOISEVOL=$400C              ;
        .define NOISEMODE=$400E             ;
        .define NOISELEN=$400F              ;
        .define DMCFREQ=$4010               ;
        .define DMCRAW=$4011                ;
        .define DMCSTART=$4012              ;
        .define DMCLEN=$4013                ;
        .define OAMDMA=$4014                ;
        .define SNDCHAN=$4015               ;
        .define CONTROL1=$4016              ;
        .define CONTROL2=$4017              ;
        .define FRAMECTRL=$4017             ;
        .define PRGROM=$8000                ;
    ;----------------------------------------




