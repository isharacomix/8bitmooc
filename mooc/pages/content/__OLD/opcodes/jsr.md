JSR (Jump to SubRoutine)
========================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Absolute         |```JSR $4400```  | $20      | 3     | 6      |

JSR is used to begin a [[subroutine]]. It behaves similarly to a [[JMP|jmp]], but
before changing the program counter, the program counter (-1) is pushed to the
[[stack]], high byte first. Subroutines usually end with the [[RTS|rts]]
subroutine.

