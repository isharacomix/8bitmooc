SBC (SuBtract with Carry)
=========================
Affects Flags: [[S|sign]] [[V|overflow]] [[Z|zero]] [[C|carry]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Immediate        |```SBC #$44```   | $E9      | 2     | 2      |
| Zero Page        |```SBC $44```    | $E5      | 2     | 3      |
| Zero Page,X      |```SBC $44,X```  | $F5      | 2     | 4      |
| Absolute         |```SBC $4400```  | $ED      | 3     | 4      |
| Absolute,X       |```SBC $4400,X```| $FD      | 3     |+4      |
| Absolute,Y       |```SBC $4400,Y```| $F9      | 3     |+4      |
| Indirect,X       |```SBC ($44,X)```| $E1      | 2     | 6      |
| Indirect,Y       |```SBC ($44),Y```| $F1      | 2     |+5      |

(+ add 1 cycle if page boundary crossed)

SBC subtracts the argument from the value in the [[accumulator]] and stores the
result in the accumulator. If the [[carry]] flag is false, and additional 1 is
taken from the result.

After computation, if the argument was greater than the value in the accumulator,
the carry flag will be cleared to show that a borrow occured. There
is no way to perform a subtract without carry, so it will often be required to use
the [[SEC|sec]] operation to set the carry flag to avoid off-by-one errors.

On most machines, if the [[decimal]] flag is set, the result will be computed in
Binary Encoded Decimal format. However, the decimal flag is disabled on the NES,
so it has no effect.

