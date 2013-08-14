JMP (JuMP)
==========
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Absolute         |```JMP $4400```  | $4C      | 3     | 3      |
| Indirect         |```JMP ($4400)```| $6C      | 3     | 5      |

JMP sets the program counter to the value specified by the argument. Normally
a [[label]] is used for absolute jumps, since you will usually be jumping to
a well-defined function.

Indirect addressing is used for advanced constructs such as
[[jump tables|jump_table]]. For indirect addressing, the argument should be
the memory location containing the low byte of the desired jump address - the
high byte will be in the following memory location. **However:** the specified
address must never be in the last byte of a page ($FF). If it is, then the
high byte will wrap around to the first byte of the page ($00), but the page
itself will not be incremented.


Example
-------
    start:
        ADC #10
        JMP skip
        SBC #10     ; This line will never be executed
    skip:
        AND #10

