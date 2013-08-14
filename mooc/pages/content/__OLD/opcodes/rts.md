RTS (ReTurn from Subroutine)
============================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```RTS```        | $60      | 1     | 6      |

RTS is the instruction used to return back to program execution after handling
a [[subroutine]]. RTS reads the program counter (low byte first) from the
[[stack]] and then continues execution from the point where the subroutine
was originally called.

