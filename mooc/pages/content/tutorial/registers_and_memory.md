Registers and Memory
====================
In this tutorial, we're going to talk about how data is stored on the NES, and
how it is understood by the 6502 processor.


What is a Byte?
---------------
On the NES, data is read, written, and moved in packages called **bytes**.
A byte is a unit of data that is made up of 8 **bits**, where each bit can either
be a 1 or a 0 (bit stands for "binary digit"). Let's look at the byte
```10110001``` as an example.

    MSB                         LSB
     7   6   5   4   3   2   1   0      MSB = Most significant byte
     1   0   1   1   0   0   0   1      LSB = Least significant byte

As you hopefully remember from the tutorial on [[binary numbers|binary_numbers]],
this byte has the value 177 in decimal ($B1 in hex). A byte is essentially a
number between 0 and 255. This means that the rightmost bit (bit 0) has the
lowest value, and the leftmost bit (bit 7) has the greatest value. We call
these bits the **least significant** and **most significant bits**, respectively.
If you've ever played games like Mario or Zelda, you may have noticed that the
maximum amount of lives or money you can carry was 255... this is why.

Sometimes you don't need to use all 8 bits. When this is the case, you can
actually store multiple values in the same byte. For example, you can split
the byte into two 4-bit containers called **nybbles**, where each nybble
can hold a value between 0 and 15. This is an effective way to fit more data
in less space, since space is tight on the NES.

    High      Low
    Nybble Nybble
    1011     0001

On the flip side, and as one might expect, it is possible to represent numbers
larger than 255 by combining bytes together. On the 6502, the way this is done
is by adding the larger byte to the right of the smaller byte. So, for example,
the number 861 would be represented by two bytes, in this order: 

    01011101 00000011

This may seem counter intuitive at first, since the numbers appear backwards
and all tangled up. However, imagine doing addition, and what it's like to
"carry the one". Since the processor reads data from left to right, it
is much easier to carry the 1 in the direction that the processor already reads
rather than trying to work backwards. While it is possible to add any number
of bytes together to make arbitrarily large numbers, two bytes together are
referred to as a **word**. Which we will discuss when we talk about...


Memory
------
**Memory** is the term given to the location that data is stored while a program
is running. From the player's score to the program code itself, memory is the
holding place for everything that makes up the game. Each byte of memory is
given a 16-bit address (two bytes... or, as we just read, a *word*), so in a
game, the byte at address ```$20A``` might be the player's remaining lives, and
```$215``` might be the vertical position of a monster on the screen.

In order to organize the memory, the 65536 possible memory **addresses** are
divided in to 256 pages of 256 bytes each. When represented in hex notation,
such as ```$4400```, the higher byte of the address ($44) represents the page
number, and the lower byte ($00) represents the byte number within that page.

Some pages in memory have special purposes. Some can store information, some are
read-only, some are especially for graphics, and some are actually connected
directly to the other hardware of the NES, such as the controller and sound
chip. The details of these pages is outlined in the [[memory map|memory_map]],
but we'll go over most of them before this tutorial is over.


Registers
---------
When data is stored in memory, it mostly remains unchanged. In order to use it
for addition, subtraction, or other kinds of manipulation, the processor needs
to take it out of memory and hold on to it. The 6502 can store 3 bytes
of data on the *processor itself* in memory locations called "registers".
Registers are like memory, except because they are located directly on the
processor, they are much faster and excellent for information that will be
changing very frequently.

When it comes down to it, programming in assembly essentially boils down to
picking up data from memory, doing something with it, and putting it back in
memory - maybe in the same place, maybe somewhere different. Rinse, lather,
repeat. When data is "picked up" it is loaded in the processor's registers in
order to be on hand for manipulation. When it is "put back", it is stored
back in memory.

Unlike memory, registers don't have addresses - they just have names: *A*, *X*,
and *Y*. The A register, also called the [[accumulator]], is the register used
most often when doing arithmetic. Operations like [[ADC|adc]] add the argument
to the value in the accumulator, and store the result in the accumulator.
Operations like [[SBC|sbc]] and [[AND|and]] behave the same way.

The *X* and *Y* registers are referred to as [[index registers|index_registers]].
Index registers are not used for arithmetic, but are often used for counting.
The [[INX|inx]] and [[DEX|dex]] arguments increase and decrease the value in the
X register by 1, while [[INY|iny]] and [[DEY|dey]] do the same thing for the
Y register.

Last, but not least, the processor also has a special 16-bit register that you
can't access directly called the **program counter**. When you assemble a program
for the NES, the binary code is stored in memory at location ```$8000```. The
program counter contains the memory address of the next instruction to be read.
When you perform a [[JMP|jmp]] or branch instruction, you are changing the value
in the program counter so that it will execute a different instruction.


Examples in Code
----------------
Let's look at the following code sample to see how memory and registers are
used on the 6502. This sample does something really silly - it just sets the
A register to "44", and adds the value in memory location ```$8``` over and
over again until it equals 100. Then it stores the A register in the memory
location ```$8 + X register```.

        LDA #44     ; This instruction says "load the value 44 into the
                    ; the A register". The "#" in front of the number means
                    ; to treat the argument as a literal value.
    loop:           ; 
        ADC $8      ; This instruction says "load the value stored at memory
                    ; address $8 and add it to the A register". Unlike the ADC
                    ; instruction above, there is no "#" sign, so the argument
                    ; is a memory location, not a literal number. The dollar
                    ; sign indicates that it is a hexadecimal number.
        CMP #100    ; This instruction says to "compare the value 100 with
                    ; the A register". Once again, the "#" symbole indicates
                    ; the 100 should be treated as a literal number.
        BEQ loop    ; This instruction says "if the result of the previous
                    ; comparison was equal, jump to the memory location of
                    ; the 'loop' label". Labels are actually shorthand for
                    ; memory addresses that correspond to where the binary
                    ; program code is located. If you were to do an "lda loop",
                    ; you would get the binary code for the "ADC" instruction
        STA $8,X    ; This instruction says "store the value in the A register
                    ; in the memory location $8 plus the X register". The index
                    ; registers are special since you can add them to instructions
                    ; like this in order to change the memory addresses used
                    ; in instructions. The X and Y registers can't be used with
                    ; the "#" symbol.

In the 6502 assembly language, all arguments to instructions are either literal
values (which start with the "#" symbol) or memory addresses.

Also, in this example, we see a special feature of the index registers - it's
possible to add them to memory locations in order to change where data is
written or read from. When they are used in this way, it is called **offset
addressing**, since the register acts as an offset to where the data is being
written. You may wonder how this could be useful... one example is when you need
to copy a single value to multiple locations.

        LDX #0      ; We are going to put "42" in all of the memory locations
        LDA #42     ; on the zero page!
    loop2:          ;
        STA $0, X   ; Store "42" at 0+X.
        INX         ; Increment the X register.
        CPX #$0     ; When the X register wraps back around to 0, we can stop.
        BNE loop2   ; Otherwise, continue looping.

This allows you to do the same thing 256 times with only six instructions. Loops
are very powerful.


Special Memory Locations
------------------------
Below, we'll cover the most important memory locations. If you are interested
in a deeper discussion, visit the [[memory map|memory_map]] page.

 * Pages $00-$07: **Random Access Memory**, or [[RAM|ram]]. This is a general
   purpose area where you can store any data for a game that you need to.
 * Page $00: The [[Zero Page|zero_page]], a special area of RAM that is faster
   to access than RAM in the other pages. This should be used for data that
   changes frequently, like position, health, lives, etc.
 * Page $01: The [[Stack|stack]], another special page of RAM. You shouldn't use
   this one. It will be explained in [[Part 5|subroutines_and_the_stack]] of
   this tutorial.
 * Page $20: Graphics Hardware Interface ([[PPU|ppu]]).
 * Page $40: Sound and Controller Interface ([[APU|apu]]).
 * Pages $80-$FF: **Program Read-Only Memory**, or [[PRG ROM|prg_rom]]. This is
   where the compiled assembly code is stored after being compiled. In general,
   this code can not be written to - only read from.
   

Navigation
----------
 * [[Next Tutorial|control_flow]]
 * [[Back to Table of Contents|tutorial]]

