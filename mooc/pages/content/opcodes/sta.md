STA (STore Accumulator)
=======================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```STA $44```    | $85      | 2     | 3      |
| Zero Page,X      |```STA $44,X```  | $95      | 2     | 4      |
| Absolute         |```STA $4400```  | $8D      | 3     | 4      |
| Absolute,X       |```STA $4400,X```| $9D      | 3     | 5      |
| Absolute,Y       |```STA $4400,Y```| $99      | 3     | 5      |
| Indirect,X       |```STA ($44,X)```| $81      | 2     | 6      |
| Indirect,Y       |```STA ($44),Y```| $91      | 2     | 6      |

STA stores the value of the [[accumulator]] in the memory location specified
by the argument.

