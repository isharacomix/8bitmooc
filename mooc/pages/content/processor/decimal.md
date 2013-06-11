Decimal Flag
============
The Decimal flag is a bit in the [[status]] register that the programmer sets
to True in order to enable Binary Coded Decimal Mode on the 6502 processor.
The Decimal Flag is disabled on the authentic NES, so most NES games begin by
using a [[CLD|cld]] instruction to turn it off for sure (just in case the
Emulator or NES clone is incorrect).

Binary Coded Decimal is a mode of operation designed to make it easier to
create displays for appliances such as digital clocks and microwaves. Normally,
one byte can contain values from 0 to 255. However, since most people expect
their clock to be displayed in decimal mode, the programmer would have to
constantly switch from hex to decimal and back.

In BCD, each [[byte|bytes]] goes from being able to support 255 numbers to 99
numbers, where the byte is split into two, 4-bit nybbles, where the high nybble
is the tens place, and the low nybble is the ones place, and these nybbles can
only range between 0 and 9.

    0000 0000   <- one byte, two nybbles
    tens ones
    
    0000 0010   <- Binary:   2 ($02), BCD:  2
    0011 1001   <- Binary:  57 ($39), BCD: 39
    1000 0001   <- Binary: 129 ($81), BCD: 81
    0010 1100   <- Binary:  44 ($2C), BCD: Error

An interesting side effect of this arrangement is that when the BCD number is
represented in hexadecimal notation, as long as all of the digits are less than
'A', you can simply remove the $ and you will be left with its BCD value.

BCD is only recognized by the [[ADC|adc]] and [[SBC|sbc]] operations, giving it
an extremely narrow use-case.

