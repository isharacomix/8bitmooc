EOR (bitwise Exclusive OR with accumulator)
===========================================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```EOR #$44```   | $49      | 2     | 2      |
| Zero Page        |```EOR $44```    | $45      | 2     | 3      |
| Zero Page,X      |```EOR $44,X```  | $55      | 2     | 4      |
| Absolute         |```EOR $4400```  | $4D      | 3     | 4      |
| Absolute,X       |```EOR $4400,X```| $5D      | 3     |+4      |
| Absolute,Y       |```EOR $4400,Y```| $59      | 3     |+4      |
| Indirect,X       |```EOR ($44,X)```| $41      | 2     | 6      |
| Indirect,Y       |```EOR ($44),Y```| $51      | 2     |+5      |

(+ add 1 cycle if page boundary crossed)

EOR performs a bitwise "xor" operation between all of the bits of the argument
and the [[accumulator]], storing the value in the accumulator. "Xor" is a boolean
operation between two bits that returns True if and only if one bit is True and
the other is False. In other words, it's True if *either bit is True, but not both*.


Truth Table
-----------
|         |True |False|
|---------|-----|-----|
|**True** |False|True |
|**False**|True |False|


Example
-------
      11000101
    ^ 00101110
      --------
      11101011


