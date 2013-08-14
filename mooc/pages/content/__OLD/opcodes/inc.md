INC (INCrement Memory)
======================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```INC $44       | $E6      | 2     | 5      |
| Zero Page,X      |```INC $44,X     | $F6      | 2     | 6      |
| Absolute         |```INC $4400     | $EE      | 3     | 6      |
| Absolute,X       |```INC $4400,X   | $FE      | 3     | 7      |

INC increases the value stored in the memory location specified by 1.

