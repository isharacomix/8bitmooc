PHA (PusH Accumulator)
======================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```PHA```        | $48      | 1     | 3      |

PHA writes the value of the [[accumulator]] to the memory location pointed to by
the [[stack pointer|stack]], and then decrements the stack pointer.

