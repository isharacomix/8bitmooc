PHP (PusH Processor status)
===========================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```PHP```        | $08      | 1     | 3      |

PHP writes the value of the processor's [[status]] flags to the memory location
pointed to by the [[stack pointer|stack]], and then decrements the stack pointer.

