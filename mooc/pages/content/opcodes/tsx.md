TSX (Transfer Stack pointer to X register)
==========================================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```TSX```        | $BA      | 1     | 2      |

TSX sets the [[X register|index_registers]] equal to the value of the
[[stack pointer|stack_pointer]].

