CMP (CoMPare Accumulator)
=========================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```CMP #$44```   | $C9      | 2     | 2      |
| Zero Page        |```CMP $44```    | $C5      | 2     | 3      |
| Zero Page,X      |```CMP $44,X```  | $D5      | 2     | 4      |
| Absolute         |```CMP $4400```  | $CD      | 3     | 4      |
| Absolute,X       |```CMP $4400,X```| $DD      | 3     |+4      |
| Absolute,Y       |```CMP $4400,Y```| $D9      | 3     |+4      |
| Indirect,X       |```CMP ($44,X)```| $C1      | 2     | 6      |
| Indirect,Y       |```CMP ($44),Y```| $D1      | 2     |+5      |

(+ add 1 cycle if page boundary crossed)

CMP performs a comparison between the argument and the [[accumulator]], setting
the flags in the [[status]] register as if a subtraction had been carried out.
In other words:
 * the [[zero]] flag is set to true if both the accumulator and the argument are equal.
 * the [[carry]] flag is set to true if the accumulator is greater than the argument

The [[sign]] flag is set as usual, and is occasionally useful, but not always the
same as a signed comparison.

