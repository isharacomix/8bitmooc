The Audio Processing Unit
=========================
The APU is a bit of a "kitchen sink" device on the NES. While it lives up to its
name by providing five sound channels to the programmer, it also contains some
other functionality, such as reading controllers and doing [[OAM]] DMA.

The APU has an internal clock that increments in ticks called "frames". Normally,
each frame will increase the clock counter by 1, and when the clock reaches 4,
then it goes back to 0. However, if bit 7 of FRAMECTRL is set to True, the
clock will take an extra frame and reset to 0 when the counter is equal to 5.

The value of the clock counter determines which of the five wave generators
is updated. Whenever the counter is three or less, the triangle wave and the
square wave envelope decays are updated. When the count is equal to 1 or 3,
the square wave frequency sweeps and length counters are updated.


The Square Waves
----------------
The APU provides two square waves, each of which are controlled by four
registers.


### SQ1VOL $4000 (SQ2VOL $4004)
This register is used to set the duty cycle and volume of the square waves.

    76543210
    ||||||||
    ||||++++- Volume (if bit 4 is 0), envelope decay rate (if bit 4 is 1)
    |||+----- Envelope Volume: write a 1 to this bit to set up an envelope
    |||       decay (makes the  . Set it to 0 to use bits 0 through 3 for the volume
    ||+------ Counter Halt: If true, this channel will play continuously and
    ||        its counter will not be decreased.
    ++------- Duty cycle: Changes the kind of sound produced by the channel


### SQ1SWEEP $4001 (SQ2SWEEP $4005)

    76543210
    ||||||||
    |||||+++- Shift count: Number of bits to shift in the frequency.
    ||||+---- Negate flag: If 0, the sweep will increase, going to higher
    ||||      frequencies. If 1, the sweep will decrease, going to lower
    ||||      frequencies. 
    |+++----- The period of the divider (higher numbers, slower sweep)
    +-------- Set to 1 to enable.


### SQ1LO $4002 (SQ2LO $4006)

    76543210
    ||||||||
    ++++++++- Low bits of the timer (pitch). Lower values correspond to
              a lower pitch.

    
### SQ1HI $4003 (SQ2HI $4007)

    76543210
    ||||||||
    |||||+++- High three bytes of the timer (pitch).
    +++++---- Length: How long the sound should play before stopping.


Triangle Wave
-------------
The triangle wave produces a softer sound compared to the square wave,
and only has 3 registers exposed to the programmer.


### TRILINEAR ($4008)

    76543210
    ||||||||
    |+++++++- 
    +-------- If true, this channel will play continuously and
              its counter will not be decreased.


### TRILO ($400A)

    76543210
    ||||||||
    ++++++++- Low bits of the timer (pitch). Lower values correspond to
              a lower pitch.



### TRIHI ($400B)

    76543210
    ||||||||
    |||||+++- High three bytes of the timer (pitch).
    +++++---- Length: How long the sound should play before stopping.


OAM DMA
-------
The Direct Memory Access for [[OAM]] is handled by the APU, and not the PPU.
Register $4014 (OAMDMA) is used for this purpose. Read the full article on OAM
for usage and behavior.


Controllers
-----------
The controllers for the NES are also controlled by the APU. In order to read
from the controllers, you start by writing a 1 to CONTROL1 ($4016) followed by
a 0. The reason for this is that by writing a 1, you open a latch on the
microcontroller in the controller itself. When this latch is open, the buttons
will turn on and off values in the controller's registers. When a zero is
written, the latch closes, and the values on the registers are frozen and
unaffected by future button presses. This process is called *strobing* the
controller port.


### CONTROL1 $4016 (CONTROL2 $4017)
After strobing the controller port, you are then able to read from player one
and player two's controllers. When you read from either controller register,
the least significant bit contains the value of the pressed button, and the
other bits are open busses, meaning that they may contain garbage data that
needs to be zeroed out (such as with the command ```AND #1```).

Since only one bit contains the information for a button press, you need to read
from the controller register eight times in order to get the state of all eight
buttons. The buttons will be read in the order **A, B, Select, Start, Up, Down,
Left, Right**. On an unmodified NES, all reads afterwards will be 0s.

