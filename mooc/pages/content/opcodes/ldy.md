LDY (LoaD Y register)
=====================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```LDY #$44```   | $A0      | 2     | 2      |
| Zero Page        |```LDY $44```    | $A4      | 2     | 3      |
| Zero Page,X      |```LDY $44,X```  | $B4      | 2     | 4      |
| Absolute         |```LDY $4400```  | $AC      | 3     | 4      |
| Absolute,X       |```LDY $4400,X```| $BC      | 3     |+4      |

(+ add 1 cycle if page boundary crossed)

LDY stores the value of the argument in the [[Y register|index_registers]].

