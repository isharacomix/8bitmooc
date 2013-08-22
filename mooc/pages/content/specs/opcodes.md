Opcodes
=======
This document covers all of the opcodes for the 6502, their usage, and their
behavior. Opcodes are human-readable mneumonics that correspond directly to
binary, machine code instructions - each opcode represents a single task that
the [[CPU]] can perform. Assembly instructions are usually broken into two
components: the opcodes (a three-letter instruction) and an argument, though
not all opcodes need an argument. The job of the assembler is to read through
all of the opcodes and convert them into machine code, which ultimately results
in an NES ROM image.

The opcodes in this list are divided into the following groups based on their
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
 * Assembler Directives
 

Load/Store Operations
---------------------
Load/Store operations are among the most commonly used operations in 6502
programming. These are used to transfer data from memory to registers and
vice versa. These are the primary opcodes you will use to interact with the
hardware through their memory-mapped registers. These operations set the
Sign and Zero flags.

### LDA (LoaD Accumulator)
    Immediate     LDA #$44      $A9  2 bytes    2 cycles
    Zero Page     LDA $44       $A5  2 bytes    3 cycles
    Zero Page,X   LDA $44,X     $B5  2 bytes    4 cycles
    Absolute      LDA $4400     $AD  3 bytes    4 cycles
    Absolute,X    LDA $4400,X   $BD  3 bytes    4+ cycles
    Absolute,Y    LDA $4400,Y   $B9  3 bytes    4+ cycles
    Indirect,X    LDA ($44,X)   $A1  2 bytes    6 cycles
    Indirect,Y    LDA ($44),Y   $B1  2 bytes    5+ cycles

### LDX (LoaD X register)
    Immediate     LDX #$44      $A2  2 bytes    2 cycles
    Zero Page     LDX $44       $A6  2 bytes    3 cycles
    Zero Page,Y   LDX $44,Y     $B6  2 bytes    4 cycles
    Absolute      LDX $4400     $AE  3 bytes    4 cycles
    Absolute,Y    LDX $4400,Y   $BE  3 bytes    4+ cycles

### LDY (LoaD Y register)
    Immediate     LDY #$44      $A0  2 bytes    2 cycles
    Zero Page     LDY $44       $A4  2 bytes    3 cycles
    Zero Page,X   LDY $44,X     $B4  2 bytes    4 cycles
    Absolute      LDY $4400     $AC  3 bytes    4 cycles
    Absolute,X    LDY $4400,X   $BC  3 bytes    4+ cycles

### STA (STore Accumulator)
    Zero Page     STA $44       $85  2 bytes    3 cycles
    Zero Page,X   STA $44,X     $95  2 bytes    4 cycles
    Absolute      STA $4400     $8D  3 bytes    4 cycles
    Absolute,X    STA $4400,X   $9D  3 bytes    5 cycles
    Absolute,Y    STA $4400,Y   $99  3 bytes    5 cycles
    Indirect,X    STA ($44,X)   $81  2 bytes    6 cycles
    Indirect,Y    STA ($44),Y   $91  2 bytes    6 cycles

### STX (STore X register)
    Zero Page     STX $44       $86  2 bytes    3 cycles
    Zero Page,Y   STX $44,Y     $96  2 bytes    4 cycles
    Absolute      STX $4400     $8E  3 bytes    4 cycles

### STY (STore Y register)
    Zero Page     STY $44       $84  2 bytes    3 cycles
    Zero Page,X   STY $44,X     $94  2 bytes    4 cycles
    Absolute      STY $4400     $8C  3 bytes    4 cycles


Register Operations
-------------------
Since many operations can only be done with the accumulator, there are operations
that allow you to move data between the registers. Furthermore, since the X and
Y registers are primarily used for counting, and not arithmetic, there are
operations specifically for incrementing and decrementing X and Y.

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
    Immediate     ADC #$44      $69  2 bytes    2 cycles
    Zero Page     ADC $44       $65  2 bytes    3 cycles
    Zero Page,X   ADC $44,X     $75  2 bytes    4 cycles
    Absolute      ADC $4400     $6D  3 bytes    4 cycles
    Absolute,X    ADC $4400,X   $7D  3 bytes    4+ cycles
    Absolute,Y    ADC $4400,Y   $79  3 bytes    4+ cycles
    Indirect,X    ADC ($44,X)   $61  2 bytes    6 cycles
    Indirect,Y    ADC ($44),Y   $71  2 bytes    5+ cycles

### SBC (SuBtract with Carry)
    Immediate     SBC #$44      $E9  2 bytes    2 cycles
    Zero Page     SBC $44       $E5  2 bytes    3 cycles
    Zero Page,X   SBC $44,X     $F5  2 bytes    4 cycles
    Absolute      SBC $4400     $ED  3 bytes    4 cycles
    Absolute,X    SBC $4400,X   $FD  3 bytes    4+ cycles
    Absolute,Y    SBC $4400,Y   $F9  3 bytes    4+ cycles
    Indirect,X    SBC ($44,X)   $E1  2 bytes    6 cycles
    Indirect,Y    SBC ($44),Y   $F1  2 bytes    5+ cycles


ADC and SBC add and subtract the argument from the value stored in the
accumulator. In addition to setting the Sign and Zero flag as expected,
the Carry flag is set to true if the result is greater than $FF and false if
otherwise. With subtraction, the Carry flag is cleared if the argument is
greater than the value in the accumulator. On the 6502, it is not possible
to do arithmetic operations without the carry bit. Therefore, it is necessary
to clear the Carry bit (CLC) before doing addition and necessary to set the
Carry bit (SEC) before doing subtraction, unless you are doing multi-byte
arithmetic.

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
All of these commands set the Sign and Zero flags, and the shifts and
rotates also set the Carry flag.

### AND (bitwise AND with accumulator)
    Immediate     AND #$44      $29  2 bytes    2 cycles
    Zero Page     AND $44       $25  2 bytes    3 cycles
    Zero Page,X   AND $44,X     $35  2 bytes    4 cycles
    Absolute      AND $4400     $2D  3 bytes    4 cycles
    Absolute,X    AND $4400,X   $3D  3 bytes    4+ cycles
    Absolute,Y    AND $4400,Y   $39  3 bytes    4+ cycles
    Indirect,X    AND ($44,X)   $21  2 bytes    6 cycles
    Indirect,Y    AND ($44),Y   $31  2 bytes    5+ cycles

### ORA (bitwise OR with Accumulator)
    Immediate     ORA #$44      $09  2 bytes    2 cycles
    Zero Page     ORA $44       $05  2 bytes    3 cycles
    Zero Page,X   ORA $44,X     $15  2 bytes    4 cycles
    Absolute      ORA $4400     $0D  3 bytes    4 cycles
    Absolute,X    ORA $4400,X   $1D  3 bytes    4+ cycles
    Absolute,Y    ORA $4400,Y   $19  3 bytes    4+ cycles
    Indirect,X    ORA ($44,X)   $01  2 bytes    6 cycles
    Indirect,Y    ORA ($44),Y   $11  2 bytes    5+ cycles

### EOR (bitwise EOR with Accumulator)
    Immediate     EOR #$44      $49  2 bytes    2 cycles
    Zero Page     EOR $44       $45  2 bytes    3 cycles
    Zero Page,X   EOR $44,X     $55  2 bytes    4 cycles
    Absolute      EOR $4400     $4D  3 bytes    4 cycles
    Absolute,X    EOR $4400,X   $5D  3 bytes    4+ cycles
    Absolute,Y    EOR $4400,Y   $59  3 bytes    4+ cycles
    Indirect,X    EOR ($44,X)   $41  2 bytes    6 cycles
    Indirect,Y    EOR ($44),Y   $51  2 bytes    5+ cycles

### ASL (Arithmetic Shift Left)
    Accumulator   ASL A         $0A  1 bytes    2 cycles
    Zero Page     ASL $44       $06  2 bytes    5 cycles
    Zero Page,X   ASL $44,X     $16  2 bytes    6 cycles
    Absolute      ASL $4400     $0E  3 bytes    6 cycles
    Absolute,X    ASL $4400,X   $1E  3 bytes    7 cycles

### LSR (Logical Shift Right)
    Accumulator   LSR A         $4A  1 bytes    2 cycles
    Zero Page     LSR $44       $46  2 bytes    5 cycles
    Zero Page,X   LSR $44,X     $56  2 bytes    6 cycles
    Absolute      LSR $4400     $4E  3 bytes    6 cycles
    Absolute,X    LSR $4400,X   $5E  3 bytes    7 cycles

### ROL (ROtate Left)
    Accumulator   ROL A         $2A  1 bytes    2 cycles
    Zero Page     ROL $44       $26  2 bytes    5 cycles
    Zero Page,X   ROL $44,X     $36  2 bytes    6 cycles
    Absolute      ROL $4400     $2E  3 bytes    6 cycles
    Absolute,X    ROL $4400,X   $3E  3 bytes    7 cycles

### ROR (ROtate Right)
    Accumulator   ROR A         $6A  1 bytes    2 cycles
    Zero Page     ROR $44       $66  2 bytes    5 cycles
    Zero Page,X   ROR $44,X     $76  2 bytes    6 cycles
    Absolute      ROR $4400     $6E  3 bytes    6 cycles
    Absolute,X    ROR $4400,X   $7E  3 bytes    7 cycles


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
    Immediate     CMP #$44      $C9  2 bytes    2 cycles
    Zero Page     CMP $44       $C5  2 bytes    3 cycles
    Zero Page,X   CMP $44,X     $D5  2 bytes    4 cycles
    Absolute      CMP $4400     $CD  3 bytes    4 cycles
    Absolute,X    CMP $4400,X   $DD  3 bytes    4+ cycles
    Absolute,Y    CMP $4400,Y   $D9  3 bytes    4+ cycles
    Indirect,X    CMP ($44,X)   $C1  2 bytes    6 cycles
    Indirect,Y    CMP ($44),Y   $D1  2 bytes    5+ cycles

# CPX (ComPare to X register)
    Immediate     CPX #$44      $E0  2 bytes    2 cycles
    Zero Page     CPX $44       $E4  2 bytes    3 cycles
    Absolute      CPX $4400     $EC  3 bytes    4 cycles

# CPY (ComPare to Y register)
    Immediate     CPY #$44      $C0  2 bytes    2 cycles
    Zero Page     CPY $44       $C4  2 bytes    3 cycles
    Absolute      CPY $4400     $CC  3 bytes    4 cycles

# BIT (test BITs)
    Zero Page     BIT $44       $24  2 bytes    3 cycles
    Absolute      BIT $4400     $2C  3 bytes    4 cycles

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

### JMP (JuMP)
    Absolute      JMP $5597     $4C  3 bytes    3 cycles
    Indirect      JMP ($5597)   $6C  3 bytes    5 cycles

JMP is an unconditional jump to a memory location. Normally most programs jump
to predefined labels, but it is also possible to do an indirect jump, where
instead of jumping to the memory location in the argument, the argument specifies
the location of the low byte of an address which is then jumped to instead. This
makes it possible to dynamically create jumps without using branching.


### JSR (Jump to SubRoutine)
    Absolute      JSR $5597     $20  3 bytes    6 cycles

### BRK (BReaK)
    Implied       BRK #$44      $00  2 bytes    7 cycles

JSR jumps to a memory location in the same way that JMP does, but in addition
to changing the program counter, it also stores the current program counter
value on the [[stack]] before jumping there. This way, after running the code that
you jump to, it is possible to return back, using the RTS instruction. BRK
is similar, in that it also performs a jump, but it ignores the argument and
jumps to the memory address in the [[vector table|vector_table]] that matches
the IRQ pointer (located at $FFFE and $FFFF). Also, the JSR instruction does not
store the processor status register on the stack, but the BRK instruction does.


### RTS (ReTurn from Subroutine)
    Implied       RTS           $60  1 bytes    6 cycles

### RTI (ReTurn from Interrupt)
    Implied       RTI           $40  1 bytes    6 cycles

RTS and RTI return to the point when a subroutine or interrupt occured.
When returning from a subroutine, the previous location of the program
counter is pulled off the stack and the program returns to its previous
operation. RTI, in addition to pulling the program counter, also pulls
the status flags (essentially a hard-coded PLP instruction).


Stack Operations
----------------
The stack, discussed in the documentation on the [[memory map|memory_map]] is
a special memory location on page $01 that can be used to add and remove data
in a specific order without saving them to literal, specific location. The
stack pointer is a register on the [[CPU]] that keeps track of where the "top"
of the stack is, and it is possible to change this value through the X register.
The stack is also used implicitly when handling subroutines and interrupt
handlers.

    TXS (Transfer X to Stack ptr)   $9A  2 cycles
    TSX (Transfer Stack ptr to X)   $BA  2 cycles
    PHA (PusH Accumulator)          $48  3 cycles
    PLA (PuLl Accumulator)          $68  4 cycles
    PHP (PusH Processor status)     $08  3 cycles
    PLP (PuLl Processor status)     $28  4 cycles
    
All of these operations are one byte in size.


Miscellaneous Operations
------------------------
There are also two other operations, INC and DEC, that don't fit in any of the
other categories, and NOP, which does absolutely nothing except safely burn
cycles.


# INC (INCrement memory)
    Zero Page     INC $44       $E6  2 bytes    5 cycles
    Zero Page,X   INC $44,X     $F6  2 bytes    6 cycles
    Absolute      INC $4400     $EE  3 bytes    6 cycles
    Absolute,X    INC $4400,X   $FE  3 bytes    7 cycles

INC simply reads the memory location, increments it, and then writes it back.
Obviously this doesn't work on ROM or memory mapped registers. INC sets the
sign and the zero flag.

    
# DEC (DECrement memory)
    Zero Page     DEC $44       $C6  2 bytes    5 cycles
    Zero Page,X   DEC $44,X     $D6  2 bytes    6 cycles
    Absolute      DEC $4400     $CE  3 bytes    6 cycles
    Absolute,X    DEC $4400,X   $DE  3 bytes    7 cycles

DEC simply reads the memory location, decrements it, and then writes it back.
Obviously this doesn't work on ROM or memory mapped registers. DEC sets the
sign and the zero flag.


# NOP (No OPeration)
    Implied       NOP           $EA  1 bytes    2 cycles

NOPs are used to kill cycles when doing carefully timed programs. When doing
extremely fancy graphics hacks, it's necessary to synchronize your code with
the picture processing unit while it is running. We won't be doing anything
that requires careful timing, so you likely won't be using this operation.


Assembler Directives
--------------------
Assembler directives aren't actually opcodes - they are commands that the
assembler can interpret and use to improve code assembly before translating
the operations into machine code.

The #8bitmooc assembler supports a few opcodes.


### .org
The .org directive tells the assembler "start putting your machine code here".
This is necessary so that when labels are calculated, they are the correct
value. This is often used to set up the [[vector table|vector_table]].

    .org $FFFA      ; This tells the assembler that the next three words
    .dw NMI         ; should be written starting at memory location $FFFA.
    .dw START       ;
    .dw IRQ         ;


### .db
### .bytes
.db allows you to put literal bytes directly in the ROM. This is usually used
when putting data such as backgrounds and palettes in the ROM to be moved into
VRAM. It is possible to write multiple values by putting commas between them.
.bytes is a synonym for .db.


### .dw
### .words
.dw is the same as .db, except instead of writing single bytes, it is used to
write two-byte words (in the proper byte order, where the low byte is placed
before the high byte). .dw is often used to put pointers to memory locations
in RAM, such as in the vector table.


### .ascii
Like .db, this writes data directly to memory, but instead of writing numbers,
writes ASCII characters, which is useful when storing dialogue or menu prompts
in the ROM. .ascii can store any string that can be enclosed in quotation marks,
but can not print quotation marks themselves.

    .ascii "Hello, world!"
    
    
### .define label=X
.define allows you to define a string as a particular number. While this can be
used to define constants, it's very useful when giving names to memory locations
so that code isn't simply a list of cryptic hexadecimal numbers.

    .define PLAYER_HP=$200
    .define PLAYER_MP=$201
    
    LDA PLAYER_HP


