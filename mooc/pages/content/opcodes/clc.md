CLC (CLear Carry)
=================
Affects Flags: [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```CLC```        | $18      | 1     | 2      |

CLC clears the [[carry]] flag regardless of its current value. This instruction
should be executed before attempting to call the [[ADC|adc]] instruction.

