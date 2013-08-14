TXS (Transfer X register to Stack pointer)
==========================================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```TXS```        | $9A      | 1     | 2      |

TXS sets the [[stack pointer|stack_pointer]] equal to the value of the
[[X register|index_registers]].

