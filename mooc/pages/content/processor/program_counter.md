Program Counter
===============
The program counter is a 16-bit register that indicates which byte in memory
will be read and exected next.

The programmer can "set" the program counter by using the [[JMP|jmp]] and
[[JSR|jsr]] opcodes, which take the argument and store them in the program
counter, effectively "jumping" to another point in code. Advanced programmers
can also use the [[RTS|rts]] instruction to read a memory address from the
[[stack]] and jump to that location.

There is no way to "read" the program counter, but it can be calculated by
performing a [[JSR|jsr]] or [[BRK|brk]] instruction, as these operations begin
by pushing the program counter to the stack. When the program counter is pushed,
the high 8 bits are pushed first.

