AND (bitwise AND with accumulator)
==================================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```AND #$44```   | $29      | 2     | 2      |
| Zero Page        |```AND $44```    | $25      | 2     | 3      |
| Zero Page,X      |```AND $44,X```  | $35      | 2     | 4      |
| Absolute         |```AND $4400```  | $2D      | 3     | 4      |
| Absolute,X       |```AND $4400,X```| $3D      | 3     |+4      |
| Absolute,Y       |```AND $4400,Y```| $39      | 3     |+4      |
| Indirect,X       |```AND ($44,X)```| $21      | 2     | 6      |
| Indirect,Y       |```AND ($44),Y```| $31      | 2     |+5      |

(+ add 1 cycle if page boundary crossed)

AND performs a bitwise "and" operation between all of the bits of the argument
and the [[accumulator]], storing the value in the accumulator. "And" is a boolean
operation between two bits that returns True if and only if both boths are True.


Truth Table
-----------
|         |True |False|
|---------|-----|-----|
|**True** |True |False|
|**False**|False|False|


Example
-------
      11000101
    & 00101110
      --------
      00000100


