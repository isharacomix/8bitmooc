RTI (ReTurn from Interrupt)
===========================
Affects Flags: All

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```RTI```        | $40      | 1     | 6      |

RTI is the instruction used to return back to program execution after handling
an interrupt. RTI begins by reading the [[status]] register from the [[stack]],
then reading the program counter (low byte first). The same rules for writing
[[subroutines|subroutine]] apply for interrupt handlers.

