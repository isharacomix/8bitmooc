TAX (Transfer Accumulator to X register)
========================================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```TAX```        | $AA      | 1     | 2      |

TAX sets the [[X register|index_registers]] equal to the value of the
[[accumulator]].

