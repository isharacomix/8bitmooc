The Audio Processing Unit
=========================
The APU is a bit of a "kitchen sink" device on the NES. While it lives up to its
name by providing five sound channels to the programmer, it also contains some
other functionality, such as reading controllers and doing [[OAM]] DMA.

The APU has several internal hardware components

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


### SQ1VOL ($4000) / SQ2VOL ($4004)
This register is used to set the duty cycle and volume of the square waves.

    76543210
    ||||||||
    ||||++++- Volume (if bit 4 is 0), envelope decay rate (if bit 4 is 1)
    |||+----- Envelope Volume: write a 1 to this bit to set up an envelope
    |||       decay (makes the sound fade out).
    ||+------ Counter Halt: If true, this channel and sweep will play continuously
    ||        and its counter will not be decreased.
    ++------- Duty cycle: Changes the kind of sound produced by the channel

The duty cycle can be one of four wave forms. Each one has a distinctive sound
to it, so picking one is like picking an instrument.

    00  _-______    (12.5%)  
    01  _--_____    (25%)
    10  _----___    (50%)
    11  -__-----    (negated 25%)


### SQ1SWEEP ($4001) / SQ2SWEEP ($4005)
A sweep is a filter applied to the waveform each frame step that either increases
or decreases the frequency of the waveform. When the sweep is able to continue
infinitely, it can either be a smooth sound or a high-paced "fluttering" effect.

    76543210
    ||||||||
    |||||+++- Shift count: Number of bits to shift in the frequency.
    ||||+---- Negate flag: If 0, the sweep will increase, going to higher
    ||||      frequencies. If 1, the sweep will decrease, going to lower
    ||||      frequencies. 
    |+++----- The period of the divider (higher numbers, slower sweep)
    +-------- Set to 1 to enable.


### SQ1LO ($4002) / SQ2LO ($4006)
This register controls the low 8 bits of the 11-bit frequency timer.

    76543210
    ||||||||
    ++++++++- Low bits of the timer (pitch). Lower values correspond to
              a higher pitch.

    
### SQ1HI ($4003) / SQ2HI ($4007)
The value written into the length counter is decreased every other frame so long
as counter has not been halted. When this counter hits zero, the sound stops
playing.

    76543210
    ||||||||
    |||||+++- High three bytes of the timer (pitch).
    +++++---- Length: How long the sound should play before stopping.


Triangle Wave
-------------
The triangle wave produces a softer sound compared to the square wave,
and only has 3 registers exposed to the programmer.


### TRILINEAR ($4008)
Unlike the square wave, which is updated every other frame step, the triangle
wave's length counter is decremented every step, meaning that it would normally
only last half as long as the square wave. However, whenever the counter hits
zero, if the counter flag is set, then the value in the lower seven bits of this
register will be loaded directly into the length counter, providing a higher
resolution counter than available to the square waves.

    76543210
    ||||||||
    |+++++++- Unlike the square wave, this is the actual counter. When it reaches
    |         zero, the reload value (in TRIHI) is loaded into here.
    +-------- If true, this channel will play continuously and its counter will
              not be decreased.


### TRILO ($400A)
This register controls the low 8 bits of the 11-bit frequency timer.

    76543210
    ||||||||
    ++++++++- Low bits of the timer (pitch). Lower values correspond to
              a higher pitch.



### TRIHI ($400B)
The value written into the length counter is decreased every frame so long
as counter has not been halted. When this counter hits zero, the sound stops
playing.

    76543210
    ||||||||
    |||||+++- High three bytes of the timer (pitch).
    +++++---- Linear counter reload. Stored in TRILINEAR when it reaches 0.


Noise Channel
-------------
The noise channel produces a static white noise, which can be used in small
bursts as a percussion instrument.

### NOISEVOL ($400C)
Very similar to the volume register of the square waves, this sets how loud the
channel playback will be.

    76543210
      ||||||
      ||++++- Volume (if bit 4 is 0), envelope decay rate (if bit 4 is 1)
      |+----- Envelope Volume: write a 1 to this bit to set up an envelope
      |       decay (makes the sound fade out).
      +------ Counter Halt: If true, this channel and sweep will play continuously
              and its counter will not be decreased.


### NOISEMODE ($400E)
This adjusts the pitch and sound of the noise generated.

    76543210
    |   ||||
    |   ++++- Period of the noise generator: lower means higher pitch.
    +-------- The mode of the channel. This changes the algorithm used to
              generate noise.


### NOISELEN ($400F)
Since there is no timer to control the pitch, this registers simply controls
the length counter.

    76543210
    |||||
    +++++---- Length: How long the sound should play before stopping.


Delta Modulation Channel
------------------------
The DMC is an advanced channel that allows the programmer to encode 1-bit delta
modulated sound to create advanced waveforms. In theory, this would enable
features like voiceovers, but in practice, requires too much space to be effective.

### DMCFREQ ($4010)
This sets the frequency and interrupts of the channel.    
    
    76543210
    ||  ||||
    ||  ++++- Frequency of playback.
    |+------- Loop flag: set to 1 to have the DMC loop
    +-------- Interrupt flag: if set to 1, the DMC will produce an IRQ when it
              finishes.


### DMCRAW ($4011)
Normally the DMC channel will read the next value from memory automatically.
This register allows you to directly load a new value into the channel. If the
timer is outputting a clock at the time you write, the write may be ignored.

        
### DMCSTART ($4012)
The address where the sample begins. The starting address is calculated in the
following way:

    %11xxxxxx xx000000

The x's represent where the value of this register are stored.


### DMCLEN ($4013)
The number of bytes in the sample. This number is multiplied by 16 and increased
by 1 to determine the number of bytes in the sample.


Sound Control
-------------
### SNDCHAN ($4015)
The sound channel register also serves as an APU status register. By writing a
zero to the bits that correspond to the sound channels, you can immediately
silence them. Writing to this register also always clears the DMC interrupt flag.

    76543210 (write)
       |||||
       ||||+- Square 1
       |||+-- Square 2
       ||+--- Triangle
       |+---- Noise
       +----- DMC

Reading from this register reports on the status of whether or not certain
channels are currently playing (their length counters are greater than zero).
It also reports on whether or not the APU is generating IRQs. When performing
an IRQ handler for the Frame counter, it is important to be sure to read this
register to clear the interrupt flag while handling to avoid an infinite loop.

    76543210 (read)
    || |||||
    || ||||+- Square 1 is currently playing
    || |||+-- Square 2 is currently playing
    || ||+--- Triangle is currently playing
    || |+---- Noise is currently playing
    || +----- DMC is currently playing
    |+------- Did a frame interrupt occur? (Reading clears this flag)
    +-------- Is the DMC interrupt flag set?


### FRAMECTRL ($4017)
This register allows the programmer to set the timing of the frame counter as
well as turn on and off IRQ generation from the Frame Counter. When IRQs are 
enabled, the program will jump to the IRQ label in the vector table on the last
step of a frame (but only when in mode 0). This is similar to the way that NMIs
are generated by the PPU when the screen refreshes. This makes it possible to
create loops for playing music. IRQs are only generated when in mode 0.

    76543210
    ||
    |+------- If set to true, do NOT generate an IRQ on step 4 of the frame.
    +-------- Clock mode. When in mode 0, there are 4 steps per frame. When in
              mode 1, there are 5 steps per frame.

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


### CONTROL1 ($4016) / CONTROL2 ($4017)
After strobing the controller port, you are then able to read from player one
and player two's controllers. When you read from either controller register,
the least significant bit contains the value of the pressed button, and the
other bits are open busses, meaning that they may contain garbage data that
needs to be zeroed out (such as with the command ```AND #1```).

Since only one bit contains the information for a button press, you need to read
from the controller register eight times in order to get the state of all eight
buttons. The buttons will be read in the order **A, B, Select, Start, Up, Down,
Left, Right**. On an unmodified NES, all reads afterwards will be 0s.

