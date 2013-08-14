Opcodes
=======
This document covers all of the opcodes for the 6502, their usage, and their
behavior. The opcodes are divided into the following groups based on their
similar behavior.

 * Load/Store
 * Register
 * Arithmetic
 * Logical
 * Comparison
 * Status Flag
 * Branching
 * Jump and Subroutine
 * Stack
 * Miscellaneous
 

Load/Store Operations
---------------------
Load/Store operations are among the most commonly used operations in 6502
programming. These are used to transfer data from memory to registers and
vice versa. These are the primary opcodes you will use to interact with the
hardware through their memory-mapped registers.

### LDA (LoaD Accumulator)

### LDX (LoaD X register)

### LDY (LoaD Y register)

### STA (STore Accumulator)

### STX (STore X register)

### STY (STore Y register)


Register Operations
-------------------
Since many operations can only be done with the accumulator, there are operations
that allow you to move data between the registers. Furthermore, since the X and
Y registers are primarily used for counting, and not arithmetic, there are
operations specifically for incrementing and decrementing X and Y.

    Operation                       Hex
    TAX (Transfer A to X)           $AA
    TXA (Transfer X to A)           $8A
    DEX (DEcrement X)               $CA
    INX (INcrement X)               $E8
    TAY (Transfer A to Y)           $A8
    TYA (Transfer Y to A)           $98
    DEY (DEcrement Y)               $88
    INY (INcrement Y)               $C8

These operations take no arguments, are one byte in length, and take two machine
cycles to run. All of these operations set the zero and sign flags normally.


Arithmetic Operations
---------------------
The 6502 has two arithmetic operations: one for addition (ADC, ADd with Carry)
and one for subtraction (SBC, SuBtract with Carry).

### ADC (ADd with Carry)

### SBC (SuBtract with Carry)

ADC and SBC add and subtract the argument from the value stored in the
accumulator. When performing an addition, the Carry flag is set to true if the
result is greater than $FF and false if otherwise. With subtraction, the Carry
flag is cleared if the argument is greater than the value in the accumulator.
On the 6502, it is not possible to do arithmetic operations without the carry
bit. Therefore, it is necessary to clear the Carry bit (CLC) before doing
addition and necessary to set the Carry bit (SEC) before doing subtraction,
unless you are doing multi-byte arithmetic.

When working with signed numbers, another flag that is necessary to use is
the Overflow flag. The overflow flag is set when the sign of the solution
doesn't match the sign of its arguments, for example, when two positive numbers,
added together, equal a negative number. When the overflow flag is set, you
*can not* assume that result of the operation is correct.

On normal 6502 chips, there is also a flag called the Decimal flag. The decimal
flag (SED and CLD) makes these opcodes encode their results in a mode called
"binary encoded decimal". This hardware was left out of the NES to avoid patent
issues, but basically the way it works is that when adding two numbers, such as
7 and 5 together, instead of the result being the hex value $0C, it instead
rolls the value up to hex $12. This mode is designed for embedded devices that
show numeric displays, like clocks or microwaves, but since it is omitted from
the NES, it is not of particular importance to us.


Logical Operations
------------------
These operations include bitwise operations such as *and*, *or*, and
*exlusive-or*, as well as bit shifts. These are very useful when reading
memory mapped registers that pack a lot of information into a single byte.

### AND (bitwise AND with accumulator)

### ORA (bitwise OR with Accumulator)

### EOR (bitwise EOR with Accumulator)

### ASL (Arithmetic Shift Left)

### LSR (Logical Shift Right)

### ROL (ROtate Left)

### ROR (ROtate Right)

AND, ORA, and EOR perform bitwise boolean operations. If you're not familiar with
boolean operations, they are operations that take two boolean values (true or
false, 1 or 0) and return a single boolean value. *and* returns true if and only
if both inputs are true. *or* returns true if either input is true. *exclusive-or*
returns true if and only if one of the inputs is true and the other is false.
The AND, ORA, and EOR opcodes apply these functions between all of the bits
of the accumulator and all of the bits of the argument.

    LDA #%10011000
    AND #%00001001
    ;A = %00001000

Let's say that you're reading from the register for Player 1's controller, $4016.
The value of the button being pressed is saved in bit #0, but it's possible that
there could be junk in the rest of the bits.

    LDA $4017
    AND #%00000001
    
This will overwrite all of the bits that you read from the register except for
the last with 0s. In fact, the AND opcode is effectively used to copy zeros
to the accumulator, while the ORA opcode is effectively used to copy ones.

The shifts and rotations do as one would expect, they simply move all of the bits
to the left or right once. The value that is shifted "out" is saved in the Carry
bit, and the value that is shifted in is either a 0 (in the case of shifts) or
the old value of the carry (in the case of a rotate). Also, the shifts and
rotations can be done directly on memory locations without having to move them
to the accumulator first.  Shifts are tremendously useful since they effectively
multiply the value by 2 (in a left shift) or divide it by 2 (in a right shift).


Comparison Operations
---------------------
Comparison operators are used to set flags such as the zero, carry, sign flags
without actually having any effect on the data in the registers or RAM.

# CMP (CoMPare to accumulator)

# CPX (ComPare to X regiseter)

# CPY (ComPare to Y regiseter)

# BIT (test BITs)


The three Compare operations simulate a subtraction between the specified
register and its argument with the intention of a branch following the
comparison. The carry flag is set when the operand is greater than or equal to
the accumulator, and is clear if it is less than the accumulator. The zero flag
is set when the two are equal (since a simulated subtraction between two equal
numbers results in 0). For this reason, BCS and BCC are often given equivalent
aliases BGE and BLT, but our assembler does not do this.

The BIT flag is a little different. Instead of simulating a subtraction, it
sets bit 0 as if the argument was ANDed with the accumulator, and sets the
sign and overflow flags equal to the values in bits 7 and 6, respectively. This
is useful in some routines on the NES where bits 7 and 6 in a memory mapped
register have important information.


Status Flag Operations
----------------------
While most flags are set automatically, there are times when you may wish to
manually set status flags. These flags and their purposes are described in more
detail in the [[CPU]] documentation.

    Operation                       Hex
    CLC (CLear Carry)               $18
    SEC (SEt Carry)                 $38
    CLI (CLear Interrupt)           $58
    SEI (SEt Interrupt)             $78
    CLV (CLear oVerflow)            $B8
    CLD (CLear Decimal)             $D8
    SED (SEt Decimal)               $F8

These operations take no arguments, are one byte in length, and take two machine
cycles to run.


Branching Operations
--------------------
A branch is a conditional jump to a location in memory based on the conditions
of the status flags. Branches work by treating their argument as a signed number
and adding it to the program counter if their condition is true. If the condition
is not true, then the branch is ignored and the program continues to the next
instruction.

    Operation                       Hex
    BPL (Branch on PLus)            $10
    BMI (Branch on MInus)           $30
    BVC (Branch on oVerflow Clear)  $50
    BVS (Branch on oVerflow Set)    $70
    BCC (Branch on Carry Clear)     $90
    BCS (Branch on Carry Set)       $B0
    BNE (Branch on Not Equal)       $D0
    BEQ (Branch on EQual)           $F0
    
Despite the operation having a one-byte argument size, it is extremely difficult
for a programmer to manually calculate the number of bytes from the branch to the
target instruction, so when you provide a label, most assemblers, including ours,
will automatically calculate the offset for you.
    
        CMP #42
        BEQ fun     ; This will calculate the distance to label "fun" from here
        JMP nofun
     fun:
        ; do stuff
    
Because the operand is only one byte in size, this means that a branch can only
go backwards or forwards by about 120 bytes. If you provide a label that exceeds
the size limit, the assembler will give you an error message so that you can
replace it with a jump.


Jump and Subroutine Operations
------------------------------
Branches are conditional jumps, but sometimes it's necessary to do unconditional
jumps to other locations in code.

### JMP

### JSR

### RTS

### RTI

### BRK


Stack Operations
----------------
The stack, discussed in the documentation on the [[memory map|memory_map]] is
a special memory location on page $01 that can be used to add and remove data
in a specific order without saving them to literal, specific location. The
stack pointer is a register on the [[CPU]] that keeps track of where the "top"
of the stack is, and it is possible to change this value through the X register.
The stack is also used implicitly when handling subroutines and interrupt
handlers.

    Operation                       Hex  Cycles
    TXS (Transfer X to Stack ptr)   $9A  2
    TSX (Transfer Stack ptr to X)   $BA  2
    PHA (PusH Accumulator)          $48  3
    PLA (PuLl Accumulator)          $68  4
    PHP (PusH Processor status)     $08  3
    PLP (PuLl Processor status)     $28  4
    
All of these operations are one byte in size.


Miscellaneous Operations
------------------------
There are also two other operations, INC and DEC, that don't fit in any of the
other categories, and NOP, which does absolutely nothing except safely burn
cycles.

# INC (INCrement memory)

# DEC (DECrement memory)

# NOP (No OPeration)


