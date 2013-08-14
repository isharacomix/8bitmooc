Zero Flag
=========
The Zero flag is a bit in the [[status]] register that is set to True whenever
the result of an operation is 0.

The [[BNE|bne]] operation branches whenever the zero bit is clear, and the
[[BEQ|beq]] operation branches whenever the zero bit is set. When the
[[CMP|cmp]] instruction is used, it simulates a subtraction, so when the argument
is the same as the value in the register, the result of the subtraction is 0,
making BEQ branch.

