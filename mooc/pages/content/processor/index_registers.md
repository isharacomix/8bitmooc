Index Registers (X and Y Registers)
===================================
The 6502 has two index registers, referred to as X and Y. Index registers
are 8-bit registers that can be used to move data back and forth between
memory, but do not support as many arithmetic operations as the [[accumulator]]
does.


Usage
-----
The index registers are primarily used for the purpose of iterating through
loops, as evidenced by the existence of the operations [[INX|inx]] and [[DEX|dex]],
which increment and decrement the X register by 1. Furthermore, both the X
and Y registers have a "compare" operation ([[CPX|cpx]]) in order to test for
when a loop terminates.

In addition to being used for loops, the index registers are also used to
manipulate memory locations in some [[addressing modes|addressing_modes]].
When performing an operation on a memory location, by adding ```,X``` or ```,Y```
to the operation, the value in the specified register will be added to the
memory address.

The index registers are also used for *indirect addressing*.
Indirect addressing is where instead of using the memory location provided by
the argument, the argument points to a location in the [[zero page|zero_page]]
that contains a value that will be used as a memory location (see the page about
[[indirect addressing|indirect_addressing]] for examples).

    LDA ($44,X)     ; Load the new memory location from $44+X
    LDA ($44),Y     ; Load the new memory location from $44, then add Y to it



Example
-------
The following code writes "42" to all of the memory locations on the zero
page. [[INX|inx]] is an operation that simply adds 1 to the X register,
since the index registers are optimized for the purpose of iterating through
loops.

        LDA #42     ; Load the value 42 into the A register
        LDX #0      ; Start the index register at 0
    loop:
        STA $0, X   ; Store 42 in [$0+X]
        INX
        CPX #0      ; Compare the X register with 0 (when it loops around)
        BNE loop    ; If the X register has not looped around yet, repeat.

