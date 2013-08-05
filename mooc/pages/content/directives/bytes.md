.bytes Directive
================
| Syntax           |
|------------------|
|```.bytes 1,2,3```|
|```.db 1,2,3```   |

The bytes directive stores a comma-separated list of literal bytes of data in
the program based on the current memory location that the assembler is
assembling to. This is often used to set up palettes or tile sprites on the
background so that the data can be copied directly from ROM to video RAM. .db
is an abbreviation for .bytes.


Example
-------
Here is an example of the entire [[palette]] table defined using the .bytes
directive.

    palette:                                ;
            .db $0F,$31,$32,$33             ;
            .db $0F,$35,$36,$37             ;
            .db $0F,$39,$3A,$3B             ;
            .db $0F,$3D,$3E,$0F             ;
            .db $0F,$28,$18,$38             ;
            .db $0F,$1C,$0C,$2C             ;
            .db $0F,$15,$05,$25             ;
            .db $0F,$02,$38,$3C             ;


