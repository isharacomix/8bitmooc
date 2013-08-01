Assembler Syntax
================
In assembly, a line of code can be made up of the following elements, all of
which are optional (a blank line is a legal line of code).

    label:  OPC argument            ; comment


Labels
------
A label is a human-readable name for a segment of code that can be jumped to
by the [[JMP|jmp]] or [[JSR|jsr]] operations. Any line can have a label.
Essentially, declaring a label creates a variable where the value is equal to
the memory location of the code when it is compiled.

You can also have multiple labels with the same value. In the following code,
label1, label2, and label3 are all equal.

    label1:
    label2:
    label3:
            ADC #44


Opcodes and Directives
----------------------
The heart of a line of code comes from the operation itself. An operation is
represented by a 3-character opcode, and represents a single instruction that
can be executed by the 6502 processor. There are 56 [[opcodes]] that the 6502
recognizes, and they are each documented in their own page in this help
document.

Many arguments also accept an argument, which is a number that usually
represents a memory location. See the page on [[addressing modes|addressing_modes]]
for more information about how these arguments are specified.

In addition to opcodes, there are also a number of assembler directives that
are like opcodes, except they are executed by the assembler rather than the
processor. Directives begin with a dot (such as [[.org|org]]).


Comments
--------
Comments are arguably the most important part of any program. Any text that
comes after a semicolon is a comment, and is ignored by the assembler. However,
because assembly code is so hard to read, comments are absolutely essential for
documenting code so that other human beings can understand what the code you
wrote does and (more importantly) why it does it.

Comments don't make your program any larger or less optimal, so you are
encouraged to explain what's going on, what assumptions you're making, and
especially what kinds of optimization tricks you are using so that your
classmates and coworkers can understand what your code is supposed to do.

These are examples of some good comments:

        ADC #2          ; Each kill gives the player two points. When the
        CMP #50         ; player has 50 points, the game is over.
        BEQ quit        ;

And here are examples of bad comments:
    
        ADC #2          ; Add 2 to the A register.
        CMP #50         ; Compare the A register with 50.
        BEQ quit        ; Jump to the quit label if they are equal.

