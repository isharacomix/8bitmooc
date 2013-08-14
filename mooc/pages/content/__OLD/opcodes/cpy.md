CPY (ComPare Y register)
=========================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```CPY #$44```   | $C0      | 2     | 2      |
| Zero Page        |```CPY $44```    | $C4      | 2     | 3      |
| Absolute         |```CPY $4400```  | $CC      | 3     | 4      |

CPY performs a comparison between the argument and the
[[Y register|index_registers]], setting the flags in the [[status]] register as
if a subtraction had been carried out. In other words:
 * the [[zero]] flag is set to true if both the Y register and the argument are equal.
 * the [[carry]] flag is set to true if the Y register is greater than the argument

The [[sign]] flag is set as usual, and is occasionally useful, but not always the
same as a signed comparison.

