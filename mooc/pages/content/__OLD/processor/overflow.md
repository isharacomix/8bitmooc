oVerflow Flag
=============
The oVerflow flag is a bit in the [[status]] register that is set to True whenever
the result of an operation is a [[signed]] overflow. In other words, if the
result of the addition or subtraction falls outside of the range 127 to -128.

The [[BVC|bvc]] operation branches whenever the overflow bit is clear, and the
[[BVS|bvs]] operation branches whenever the overflow bit is set. There is no way
to simply set the overflow flag, but it can be cleared with [[CLV|clv]]. 

