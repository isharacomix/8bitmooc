BPL (Branch on PLus)
====================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Relative         |```BPL $44```    | $10      | 2     |~2      |

BPL increments the the program counter by the argument (signed) if and only
if the [[sign]] flag is cleared. The addressing mode is relative, meaning that
any given branch can only jump back or forward by about 128 bytes. If you need
to jump farther than that, you'll have to use a [[JMP|jmp]] instruction.

When the CPU reads this instruction, it performs a relative jump. However, the
assembler allows you to specify an absolute label as the argument instead, and
*it calculates the relative offset for you* so that you don't have to manually
count the instructions.

A branch not taken takes 2 cycles. A branch taken takes 3, and if the jump
crosses a page of memory, an additional cycle is taken.
