.ascii Directive
================
| Syntax                    |
|---------------------------|
|```.ascii "Hello, world!```|

The .ascii directive stores raw bytes that correspond to the ASCII codes for
a quoted string into the program based on the current memory location that the
assembler is assembling to. This is an approach for storing strings in memory
that can be good for creating character dialog and displaying messages to the
player.

