BIT (test BITs)
===============
Affects Flags: [[S|sign]] [[V|overflow]] [[Z|zero]]

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Zero Page        |```BIT $44```    | $24      | 2     | 3      |
| Absolute         |```BIT $4400```  | $2C      | 3     | 4      |

The BIT flag is used to test multiple bits at once. The [[zero]] flag is set as
though the argument was [[AND|and]]ed with the [[accumulator]]. The [[sign]] and
[[overflow]] flags are set to equal the values of the 7th and 6th bit in the
tested address, respectively.

