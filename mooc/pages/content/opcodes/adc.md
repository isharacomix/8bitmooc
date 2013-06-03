ADC (ADd with Carry)
====================

Affects Flags: [[S|sign]] [[V|overflow]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```ADC #$44```   | $69      | 2     | 2      |
| Zero Page        |```ADC $44```    | $65      | 2     | 3      |
| Zero Page,X      |```ADC $44,X```  | $75      | 2     | 4      |
| Absolute         |```ADC $4400```  | $6D      | 3     | 4      |
| Absolute,X       |```ADC $4400,X```| $7D      | 3     |+4      |
| Absolute,Y       |```ADC $4400,Y```| $79      | 3     |+4      |
| Indirect,X       |```ADC ($44,X)```| $61      | 2     | 6      |
| Indirect,Y       |```ADC ($44),Y```| $71      | 2     |+5      |

+ add 1 cycle if page boundary crossed

ADC adds the argument to the the value in the [[accumulator]] and stores the
result in the accumulator. If the [[carry]] flag is true, and additional 1 is
added to the result.

After computation, if the sum is greater than $FF, the carry flag will be set
to true, and the low 8 bits of the result will remain in the accumulator.


