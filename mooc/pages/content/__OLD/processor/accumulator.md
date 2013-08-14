Accumulator (The A Register)
============================
In assembly programming, the *accumulator* is the name given to the [[register]]
used as the working space for operations such as arithmetic.

On the 6502, the Accumulator is simply called the *A register*, and is the only
register used in operations such as [[addition|adc]] and [[subtraction|sbc]].
When performing an addition operation, the value of the argument is added to the
value that is already in the A register, and then the value of the result is
stored in the A register.

Data can be moved between the accumulator and the
[[index registers|index_registers]] using the [[TAX|tax]], [[TAY|tay]],
[[TXA|txa]], and [[TYA|tya]] opcodes.

