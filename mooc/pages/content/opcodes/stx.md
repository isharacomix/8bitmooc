STX (STore X register)
======================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```STX $44```    | $86      | 2     | 3      |
| Zero Page,Y      |```STX $44,Y```  | $96      | 2     | 4      |
| Absolute         |```STX $4400```  | $8E      | 3     | 4      |

STX stores the value of the [[X register|index_registers]] in the memory
location specified by the argument.

