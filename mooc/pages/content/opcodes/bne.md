BNE (Branch on Not Equal)
=========================
Affects Flags: None

| Addressing Mode  | Usage           | Hex Code | Bytes |Cycles  |
|------------------|-----------------|---------:|------:|-------:|
| Relative         |```BNE $44```    | $D0      | 2     |~2      |

BNE increments the the program counter by the argument (signed) if and only
if the [[zero]] flag is clear. The addressing mode is relative, meaning that
any given branch can only jump back or forward by about 128 bytes. If you need
to jump farther than that, you'll have to use a [[JMP|jmp]] instruction.

When the CPU reads this instruction, it performs a relative jump. However, the
assembler allows you to specify an absolute label as the argument instead, and
*it calculates the relative offset for you* so that you don't have to manually
count the instructions.

A branch not taken takes 2 cycles. A branch taken takes 3, and if the jump
crosses a page of memory, an additional cycle is taken.

