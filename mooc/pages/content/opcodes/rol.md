ROL (ROtate Left)
=================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Accumulator      |```ROL A      ```| $2A      | 1     | 2      |
| Zero Page        |```ROL $44    ```| $26      | 2     | 5      |
| Zero Page,X      |```ROL $44,X  ```| $36      | 2     | 6      |
| Absolute         |```ROL $4400  ```| $2E      | 3     | 6      |
| Absolute,X       |```ROL $4400,X```| $3E      | 3     | 7      |


ROL moves all of the bits in the location in the argument one place to the left.
The value in the [[carry]] is pushed into the rightmost bit, and the value in
the leftmost bit is saved in the carry.


Example
-------
      11000101 (carry = 1)
    (after ROL)
      10001010 (carry = 1)

