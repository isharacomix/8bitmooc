PLA (PuLl Accumulator)
======================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```PLA```        | $68      | 1     | 4      |

PLA increments the [[stack pointer|stack]] and then sets the [[accumulator]]
equal to the value in memory pointed to by the stack pointer.

