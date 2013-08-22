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

