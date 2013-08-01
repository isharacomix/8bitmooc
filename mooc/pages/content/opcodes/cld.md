CLD (CLear Decimal)
===================
Affects Flags: [[D|decimal]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Implied          |```CLD```        | $D8      | 1     | 2      |

CLD clears the [[decimal]] flag, which turns off decimal-encoded binary mode,
which - incidentally - the NES does not support. In general, it is a good idea
to begin every program with a CLD command.

