.org Directive
==============
| Syntax         |
|----------------|
|```.org $C000```|

The .org directive tells the assembler to begin assembling code at a
specific point in memory. For example in the following code sample:

    .org $C000
    ADC #44
    .org $D000
    SBC #88
 
the binary code associated with the ```ADC``` instruction will be
located at memory location $C000, and the binary code associated with the
```SBC``` instruction will be located at memory location $D000. If we
wanted to create a ```JMP``` instruction, we could give it the argument $D000,
and it would then execute the ```SBC #88``` instruction.


Example
-------
The .org directive is often used in order to set the [[vector table|vector_table]]
located at memory location $FFFA.

    ; ...
    ; code goes here
    ; ...
    
    .org $FFFA
    .dw nmi
    .dw start
    .dw break

