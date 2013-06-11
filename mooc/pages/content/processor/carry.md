Carry Flag
==========
The Carry flag is a bit in the [[status]] register that is set to True whenever
the result of an addition is greater than 255, and is set to False when the
result of a subtraction is less than 0. The primary purpose of the carry flag
is to support arithmetic for numbers greater than 8 bits wide.

The [[BVC|bvc]] operation branches whenever the carry bit is clear, and the
[[BVS|bvs]] operation branches whenever the carry bit is set. As all addition
and subtraction uses the carry flag, it should be cleared with [[CLC|clc]]
before an addition and set with [[SEC|sec]] before a subtraction.

