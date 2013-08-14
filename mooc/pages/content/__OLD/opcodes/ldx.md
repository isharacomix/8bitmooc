LDX (LoaD X register)
=====================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```LDX #$44```   | $A2      | 2     | 2      |
| Zero Page        |```LDX $44```    | $A6      | 2     | 3      |
| Zero Page,Y      |```LDX $44,Y```  | $B6      | 2     | 4      |
| Absolute         |```LDX $4400```  | $AE      | 3     | 4      |
| Absolute,Y       |```LDX $4400,Y```| $BE      | 3     |+4      |

(+ add 1 cycle if page boundary crossed)

LDX stores the value of the argument in the [[X register|index_registers]].

