What is Assembly Language?
==========================
If you've ever programmed a game before, you probably used a programming
language to do it. You may have written games in Python, Flash, C, or
Javascript, which are all considered **high-level** programming languages.
High-level languages are languages that take advantage of the computer's
operating system in order to make advanced programming easier.

The NES does not have an operating system, and has a very limited amount of
memory to work with, so it is not possible (or at best, very difficult) to
write programs in a high-level language for them. Therefore, we use the
opposite - a low-level language referred to as an **assembly language**
(abbreviated as "ASM"). Assembly languages are a human-readable language where
the programmer writes the operations that the computer will perform in exactly
the way that the computer would perform it.

Example
-------
Here is an example of a loop in a high-level language, C. This code simply
'does something' 100 times.

    number = 0;
    while ( number < 100 )
    {
        do_something();
        number = number + 1;
    }

The reason why we call this a high level language is because there is no
computer that exists that understands "while".

        LDX #0              ; number = 0
    loop:                   ; 
        JSR do_something    ; "do something"
        INX                 ; increase number by 1
        CPX #100            ; check if number is not equal to 100
        BNE loop            ; if it is not equal, jump back to the loop
        
The assembly version is somewhat more cryptic, but much more explicit. It
defines *exactly* what the computer has to do. It will store the number 0 in
a [[register]], it will 'do something'. It will increase the value in the
register, compare that register with the value 100, and - if it is not equal -
do the loop again.

**High level languages tell the computer what to do. Assembly languages tell the
computer exactly how to do it.**


The CPU
-------
The heart of the NES lies in its Central Processing Unit (CPU), the **MOS 6502**.
The 6502 was a processor that was used in several home computers during the 1980s,
such as the Apple ][, the Commodore 64 and even the Atari 2600.

All processors have what is called an **instruction set** - an exhaustive list
of everything that the processor can possibly do. This includes things such as
addition and subtraction, to things as simply as moving data in and out of
[[memory]]. The instruction set is encoded in binary, and specifies how the CPU
will behave when it reads certain binary values from memory while the computer
is running.

An assembly language is a language that allows programmers to write programs
using the processor's instruction set, but without having to write in binary.
For example, on the 6502, when the binary sequence ```11101000`` is read,
it increases the value of the X register by 1. However, in assembly, this
instruction is represented by a human-readable **opcode**: *INX* (which stands
for *INcrement X*).

Every processor has its own assembly language with opcodes for its own
instruction set. The 6502 Assembly language is very small, with a total of 56 
[[opcodes]], each of which has its own page in these help pages explaining how
it works.


Opcodes and Arguments
---------------------
One of the most important resources for an assembly programmer


Navigation
----------
 * [[Next Tutorial|registers_and_memory]]
 * [[Back to Table of Contents|tutorial]]

