ASL (Arithmetic Shift Left)
===========================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Accumulator      |```ASL A```      | $0A      | 1     | 2      |
| Zero Page        |```ASL $44```    | $06      | 2     | 5      |
| Zero Page,X      |```ASL $44,X```  | $16      | 2     | 6      |
| Absolute         |```ASL $4400```  | $0E      | 3     | 6      |
| Absolute,X       |```ASL $4400,X```| $1E      | 3     | 7      |

ASL moves all of the bits in the location in the argument one place to the left.
A zero will be pushed into the rightmost bit, and the leftmost bit will be saved
in the [[carry]].

This effectively multiplies the value in location in the argument by 2.


Example
-------
      11000101
    (after ASL)
      10001010 (carry = 1)

