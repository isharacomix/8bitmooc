STY (STore Y register)
======================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```STY $44```    | $84      | 2     | 3      |
| Zero Page,X      |```STY $44,X```  | $94      | 2     | 4      |
| Absolute         |```STY $4400```  | $8C      | 3     | 4      |

STY stores the value of the [[Y register|index_registers]] in the memory
location specified by the argument.

