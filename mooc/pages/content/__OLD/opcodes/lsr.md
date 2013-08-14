LSR (Logical Shift Right)
=========================
Affects Flags: [[S|sign]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Accumulator      |```LSR A```      | $4A      | 1     | 2      |
| Zero Page        |```LSR $44```    | $46      | 2     | 5      |
| Zero Page,X      |```LSR $44,X```  | $56      | 2     | 6      |
| Absolute         |```LSR $4400```  | $4E      | 3     | 6      |
| Absolute,X       |```LSR $4400,X```| $5E      | 3     | 7      |


LSR moves all of the bits in the location in the argument one place to the right.
A zero will be pushed into the leftmost bit, and the rightmost bit will be saved
in the [[carry]].

This effectively divides the value in location in the argument by 2.


Example
-------
      11000101
    (after LSR)
      01100010 (carry = 1)


Logical vs Arithmetic
---------------------
In a shift to the left, there is no difference between a logical and an
arithmetic shift to the left (so [[ASL|asl]] could be called LSL without being
untrue). On the other hand, a logical shift to the right treats the value being
shifted as unsigned, where a zero is pushed into the leftmost bit. In an
arithmetic shift to the right, the value is treated as signed, meaning that the
value that was originally in the leftmost bit will be pushed into the leftmost
bit again.

The 6502 doesn't provide an ASR. However, you can simulate it using the
[[BIT|bit]] instruction.

        LSR $4000   ; Move all bits to the right. The leftmost bit is now the 6th.
        BIT $4000   ; Sets the [[overflow]] flag to the 6th bit.
        BVC not_neg ; If the 6th bit is a zero, we're done 
        ORA #$80    ; Otherwise, set the 7th bit to 1.
    not_neg:
        ;...code...


