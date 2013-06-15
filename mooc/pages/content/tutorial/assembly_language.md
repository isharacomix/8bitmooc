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
Here is an example of a loop in a high-level language, C. Don't worry if you
don't completely understand it - just know that this code simply 'does
something' 100 times.

    number = 0;
    while ( number < 100 )
    {
        do_something();
        number = number + 1;
    }

The reason why we call this a high level language is because a computer has
no concept of 'while', and the idea of 'while' has to be broken down into
smaller instructions that the computer can do, step-by-step.

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
Assembly language is deceptively easy to write and read, especially when the
programs are small. When the processor is running, it will read one line of
code at a time from bottom to top, unless the processor is told to **jump** or
**branch** somewhere else. A line of assembly code looks something like

    label:     instruction            ; comment

Any (or all) of the above elements can be omitted (blank lines are valid).
Below, we'll discuss in detail what each of these elements are.


### Labels
Labels are used section off segments of code based on what they do. For example,
a program may contain a ```start``` label to show where the program begins, a
```controller``` label to identify the code that handles the input from the player,
and a ```draw``` label to show where the code that displays sprites on the screen
is located.

These labels are not just for readability. They also represent places in the
code where you can jump to. For example, in the assembly example above, there
is a label named ```loop```, and whenever X is less than 100, the program jumps back
to that label until X reaches 100 ([[BNE|bne]] stands for "Branch if Not Equal").
This topic will be covered in part 4 of the tutorial, [[Control Flow|control_flow]].


### Instructions
The heart of a line of code is in its instruction, which itself is made up of an
opcode and (sometimes) an argument. As discussed earlier, an opcode is a single
instruction that a processor knows how to execute. In the example code above,
we've seen several opcodes, some with arguments and some without.

For example, the [[CPX|cpx]] (ComPare X) instruction compares the value in
the X register to a number specified by the programmer. The ```#100```, the
number that the X register is being compared to, is called the **argument**.
The next instruction, [[BNE|bne]] (Branch if Not Equal), is an opcode that will
tell the processor to jump to a new location if the result of a comparison found
that the two compared values were NOT equal (and will do nothing if they are).
The argument here is the label ```loop```, the label that should be jumped to
if the comparison is unequal.

[[INX|inx]] (INcrement X), on the other hand, doesn't need an argument since
it always does the same thing - it adds 1 to the value currently in the X
register.


### Comments
Comments are, quite possibly, the most important part of any program. Comments
are completely ignored by the processor, meaning that they are a great place to
describe what your program is doing. Assembly instructions are extremely
detailed, and it's easy to get lost in what's happening if you start in the
middle of them somewhere. Comments allow the programmer to explain what is going
on, in English, and why they used the instructions they did.

For example, compare these comments

    loop:                   ; loop label
        JSR do_something    ; jump to the do_something subroutine
        INX                 ; increase x by 1
        CPX #100            ; compare x to #100
        BNE loop            ; jump if not equal

to these...

    loop:                   ;  -- BEGIN "loop"
        JSR do_something    ; There are 100 tiles on the screen, so we use
        INX                 ; the X register to loop through and draw them
        CPX #100            ; with the "do_something" subroutine.
        BNE loop            ;  -- END OF "loop"

Which code would you rather have to read and debug?


Try it yourself
---------------
Visit one of the games in the [Arcade](/arcade/) and click on the "source"
button. This will copy the source code of the game into the [[playground]] and
allow you to see the code behind it, including comments. Find arguments that
have opcodes and try changing them to see how it affects the program.

Remember that the processor can't read the same human-readable assembly that we
can. Whenever you click the "assemble" button, it converts the assembler
directly into a binary image that is essentially a virtual NES cartridge, and
then simulates the 6502 processor in order to display the game. You should try
to get comfortable with changing values and seeing how it affects the games in
the arcade, even if you don't completely understand how they work.


Navigation
----------
 * [[Next Tutorial|registers_and_memory]]
 * [[Back to Table of Contents|tutorial]]

