CPX (ComPare X register)
=========================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```CPX #$44```   | $E0      | 2     | 2      |
| Zero Page        |```CPX $44```    | $E4      | 2     | 3      |
| Absolute         |```CPX $4400```  | $EC      | 3     | 4      |

CPX performs a comparison between the argument and the
[[X register|index_registers]], setting the flags in the [[status]] register as
if a subtraction had been carried out. In other words:
 * the [[zero]] flag is set to true if both the X register and the argument are equal.
 * the [[carry]] flag is set to true if the X register is greater than the argument

The [[sign]] flag is set as usual, and is occasionally useful, but not always the
same as a signed comparison.

