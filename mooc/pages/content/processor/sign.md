Sign Flag
=========
The Sign flag is a bit in the [[status]] register that is set to True whenever
the result of an operation is negative (in other words, if the leftmost bit
is 1). The sign flag is usually abbreviated as "S", but some tutorials call it
the "Negative" flag, abbreviating it as "N".

The [[BPL|bpl]] operation branches whenever the sign bit is clear, and the
[[BMI|bmi]] operation branches whenever the sign bit is set.

