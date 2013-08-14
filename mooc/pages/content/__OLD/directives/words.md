.words Directive
================
| Syntax                       |
|------------------------------|
|```.words $1001,$2002,$3003```|
|```.dw $1001,$2002,$3003```   |

The .words directive stores a comma-separated list of literal words of data in
the program based on the current memory location that the assembler is
assembling to. This is often used to store memory locations, since memory
locations are one word (two bytes) long, and have to be stored in little-endian
order (the word $1001 would be stored in memory as $01, $10). This automatically
takes care of storing the bytes in the correct endianness.


Example
-------
The .words directive is often used in order to set the [[vector table|vector_table]]
located at memory location $FFFA.

    ; ...
    ; code goes here
    ; ...
    
    .org $FFFA
    .dw nmi
    .dw start
    .dw break

