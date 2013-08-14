PLP (PuLl Processor status)
===========================
Affects Flags: All

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```PLP```        | $28      | 1     | 4      |

PLP increments the [[stack pointer|stack]] and then sets the processor's
[[status]] register equal to the value in memory pointed to by the stack
pointer.

