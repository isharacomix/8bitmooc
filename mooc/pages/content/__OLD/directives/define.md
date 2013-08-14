.define Directive
=================
| Syntax              |
|---------------------|
|```.define life=42```|

The .define directive tells the assembler to replace all occurences of a certain
string with a literal number. Defined numbers are basically equivalent to
[[labels|label]] and can be used as memory locations, constants, and in
arithmetic.


Example
-------
The .define directive is often used to name memory locations, similar to the way
that variables are named in other languages.

    .define P1_X=$300
    .define P1_Y=$301
    .define START_X=50
    .define START_Y=30
    
    LDX #START_X        ; This loads the literal starting positions into the
    LDY #START_Y        ; X and Y registers. Note the syntax differences.
    STX P1_X            ; This stores those values in the memory locations
    STY P1_Y            ; indicated as the X and Y positions of player 1.

