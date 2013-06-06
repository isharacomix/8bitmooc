DEC (DECrement Memory)
======================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```DEC $44```    | $C6      | 2     | 5      |
| Zero Page,X      |```DEC $44,X```  | $D6      | 2     | 6      |
| Absolute         |```DEC $4400```  | $CE      | 3     | 6      |
| Absolute,X       |```DEC $4400,X```| $DE      | 3     | 7      |

DEC reduces the value stored in the memory location specified by 1.

