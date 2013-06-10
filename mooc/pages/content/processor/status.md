Status Register
===============
The status register is an 8-bit register that contains *status flags*, which are
single bits that contain information about the result of an instruction.

    7   6   5   4   3   2   1   0
    S   V   -   B*  D   I   Z   C

 * Bit 7, [[Sign|sign]]: The S flag is set to True whenever the result of an
   operation is negative.
 * Bit 6, [[oVerflow|overflow]]: The V flag is set to True whenever a signed
   overflow occurs.
 * Bit 5: Not used
 * Bit 4, [[Break|break]]: The B flag is a special case that indicates the
   occurence of an software interrupt. It is not a bit on the processor, but
   appears when interrupts push the status flags to the [[stack]].
 * Bit 3, [[Decimal|decimal]]: The D flag is a flag set by the programmer
   that toggles binary-encoded-decimal mode. On the NES, this flag is ignored.
 * Bit 2, [[Interrupt|interrupt]]: The I flag is a flag set by the programmer
   to disable maskable interrupts, such as those produced by the [[APU|apu]].
 * Bit 1, [[Zero|zero]]: The Z flag is set to True whenever the result of an
   operation is 0.
 * Bit 0, [[Carry|carry]]: The C flag is set to True whenever an unsigned
   overflow occurs.

Whenever an interrupt occurs, the processor pushes the status flags to the
stack in this order as a single byte. Similarly, the [[PLP|plp]] instruction
reads the top byte of the stack and maps its bits to the processor flag as
specified above.

