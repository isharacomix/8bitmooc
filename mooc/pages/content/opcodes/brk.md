BRK (BReaK)
===========
Affects Flags: [[B|break]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```BRK #$44```   | $00      | 2     | 7      |

The BRK instruction performs a "software interrupt" and increments the program
counter by one. The software interrupt will begin the subroutine pointed to by
the memory location ```$FFFE``` in the [[vector table|vector_table]]. Just like a
[[interrupt]], three values are pushed to the [[stack]] when the interrupt begins:
the high byte of the program counter, the low byte of the program counter, and
the [[status]] register, in that order.

The "argument" of the subroutine is not actually read by the processor... as
stated earlier, it is literally skipped over. However, it's possible to look at
the memory address pushed to the stack (minus one) and use that to use the byte
to define "different interrupts".

