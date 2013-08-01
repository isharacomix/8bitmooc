Stack Pointer
=============
The stack pointer is an 8-bit register that indicates the current location of
the top of the [[stack]]. The location pointed to by the stack pointer is
supposed to be "empty", meaning that whenever a byte is pushed to the stack,
the byte is written to the address pointed to by the stack pointer, and then
the stack pointer is decremented (since the stack grows downward).

The stack pointer can be read and changed using the [[TSX|tsx]] and [[TXS|txs]]
operations, that allow the stack pointer to be transferred through the
[[X register|index_registers]].

