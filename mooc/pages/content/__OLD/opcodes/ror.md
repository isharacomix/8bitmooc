ROR (ROtate Right)
==================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Accumulator      |```ROR A```      | $6A      | 1     | 2      |
| Zero Page        |```ROR $44```    | $66      | 2     | 5      |
| Zero Page,X      |```ROR $44,X```  | $76      | 2     | 6      |
| Absolute         |```ROR $4400```  | $6E      | 3     | 6      |
| Absolute,X       |```ROR $4400,X```| $7E      | 3     | 7      |

ROR moves all of the bits in the location in the argument one place to the right.
The value in the [[carry]] is pushed into the leftmost bit, and the value in
the rightmost bit is saved in the carry.


Example
-------
      11000101 (carry = 1)
    (after ROR)
      11100010 (carry = 0)

