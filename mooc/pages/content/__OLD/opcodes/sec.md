SEC (SEt Carry)
===============
Affects Flags: [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```SEC```        | $38      | 1     | 2      |

SEC sets the [[carry]] flag regardless of its current value. This instruction
should be executed before attempting to call the [[SBC|sbc]] instruction.

