The 6502 Microprocessor
=======================
At the heart of the NES is the MOS Technology 6502 CPU, the chip of the machine
responsible for reading the NES game cartridges and turning them into fun.
The 6502 interacts with the [[PPU]] and the [[APU]]


Registers
---------
Registers are memory locations built into the 6502 that can hold one byte of
data each. There are three general purpose registers on the 6502 that can be
used by the programmer freely, and three special purpose registers used
internally by the hardware. Understanding the role of the registers makes it
possible to understand the different features available to the programmer.


### Accumulator (A)
The accumulator is the register used for all arithmetic calculations. When doing
addition, subtraction, etc, the argument of the operation is added or subtracted
from the value in the accumulator and then the result is saved in the accumulator.


### Index Registers (X, Y)
The index registers are primarily used for counting and looping. While they can
not be used for addition and subtraction, they feature an increment (INX, INY)
and decrement (DEX, DEY) operation, allowing the programmer to increase or
decrease their values by 1.

The name for these registers come from two addressing modes they can be used in.
The first is *indexed addressing*, which allows you to add the value in the
register to a memory location and load/store data from that memory location.

    LDX #5              ;
    LDY #10             ; 
    LDA $3300           ; Load the value in $3300 into A
    LDA $3330,X         ; Load the value in $3305 ($3300+X) into A

The second mode, which is even more powerful, is called *indirect addressing*,
which is a form of addressing where instead of specifying the memory location
of the data, you specify the memory location of a *pointer* to the data, and
the data is accessed dynamically.

    ; assume that $00 holds the value #$33
    ;             $01 holds the value #$44
    ;             $02 holds the value #$55
    LDX #0              ;
    LDA ($00,X)         ; This will load the value at $4433
    LDX #1              ;
    LDA ($00,X)         ; This will load the value at $5544   
    LDY #1              ;
    LDA ($00),Y         ; This will load the value at $4434

These addressing modes are very useful when trying to do object oriented
programming. For example, the pointers may hold the addresses of different
characters in an RPG, and a subroutine for attacking may be able to use these
addresses to access where the character's various stats are without having to
know where in memory they are stored in advance. Advanced tutorials will cover
these addressing modes.


### Processor Status (PS)
The status register is a special register that contains a number of 1 bit *flags*
that contain information about the results of executing opcodes. Since these
flags are 1 bit, the only values they can hold are True and False. Some tutorials
refer to a True flag as a *set* flag and a False flag as a *clear* flag.
The flags are defined as follows:

    SV-BDIZC
    76543210
    || |||||
    || ||||+- Carry flag: This flag is set to True whenever an unsigned overflow
    || ||||   occurs.
    || |||+-- Zero flag: This flag is set to True whenever the result of a load
    || |||    or arithmetic operation results in 0.
    || ||+--- Interrupt flag: when this flag is set to True by the programmer,
    || ||     maskable interrupt requests are ignored.
    || |+---- Decimal flag: this flag is set to True by the programmer when
    || |      programming using binary-coded decimal mode. The NES ignores this
    || |      flag
    || +----- Break flag: a special flag that does not actually exist on the
    ||        PS register, but on the stack after a BRK instruction occurs
    |+------- oVerflow flag: set to True whenever an overflow occurs after
    |         an arithmetic operation
    +-------- Sign flag: set to True whenever the result of an operation is
              negative (bit 7 is 1)

These flags are tested with the various branch opcodes (such as Branch if Carry
Clear) to perform conditional logic. For example, if we want to loop exactly
twenty times we can load the number 20 into the X register and decrement it each
time we go through the loop. Since DEX sets the zero flag, the zero flag will
become True when the loop is over, and we can BEQ out of the loop.


### Program Counter (PC)
The program counter contains the memory address of the current instruction
that will be executed.

The JMP and JSR [[opcodes]] allow the programmer to set this register directly,
and branching operations make it possible to modify it. When jumping to a
subroutine or handling an interrupt, this value is pushed to the stack so that
it can be retrieved and the program can resume where it left off before the
interruption.


### Stack Pointer (SP)
The stack pointer points to the top of the stack, which is located on page 1
of the [[memory map|memory_map]]. The stack is a special page of memory that
allows you to store and load memory by *pushing* and *pulling* data to and from
it.

When data is *pushed*, it is stored at the memory location on page 1 equal to the
value of the stack pointer. After pushing, the stack pointer is decreased by 1
so that the next piece of data can be stored below it. When data is *pulled*,
the stack pointer is increased by 1 and then the value where the stack is pointing
is returned.

The stack pointer can be changed using the TXS and TSX opcodes, which allow the
programmer to transfer values between the stack pointer and X register. When
doing a subroutine, the program counter is pushed to the stack implicitly, but
the programmer can manually push and pull values using the accumulator, as well
as pushing and pulling the values of the status register.


Interrupts
----------


