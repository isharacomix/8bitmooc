ORA (bitwise OR with Accumulator)
==================================
Affects Flags: [[S|sign]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```ORA #$44   ```| $09      | 2     | 2      |
| Zero Page        |```ORA $44    ```| $05      | 2     | 3      |
| Zero Page,X      |```ORA $44,X  ```| $15      | 2     | 4      |
| Absolute         |```ORA $4400  ```| $0D      | 3     | 4      |
| Absolute,X       |```ORA $4400,X```| $1D      | 3     |+4      |
| Absolute,Y       |```ORA $4400,Y```| $19      | 3     |+4      |
| Indirect,X       |```ORA ($44,X)```| $01      | 2     | 6      |
| Indirect,Y       |```ORA ($44),Y```| $11      | 2     |+5      |

(+ add 1 cycle if page boundary crossed)

ORA performs a bitwise "or" operation between all of the bits of the argument
and the [[accumulator]], storing the value in the accumulator. "Or" is a boolean
between two bits that returns True if and only if either bit is True.


Truth Table
-----------
|         |True |False|
|---------|-----|-----|
|**True** |True |True |
|**False**|True |False|


Example
-------
      11000101
    | 00101110
      --------
      11101111


