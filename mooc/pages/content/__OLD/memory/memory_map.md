

Code
----
Below is code you can copy and paste into your programs so that you don't have
to read and write from arbitrary memory locations. This should be after your
first documentation, but before running any code.

    .define ZEROPAGE=$0000
    .define STACK=$0100
    .define PPUCTRL=$2000
    .define PPUMASK=$2001
    .define PPUSTATUS=$2002
    .define OAMADDR=$2003
    .define OAMDATA=$2004
    .define PPUSCROLL=$2005
    .define PPUADDR=$2006
    .define PPUDATA=$2007
    .define SQ1VOL=$4000
    .define SQ1SWEEP=$4001
    .define SQ1LO=$4002
    .define SQ1HI=$4003
    .define SQ2VOL=$4004
    .define SQ2SWEEP=$4005
    .define SQ2LO=$4006
    .define SQ2HI=$4007
    .define TRILIN=$4008
    .define TRILO=$400A
    .define TRIHI=$400B
    .define NOISEVOL=$400C
    .define NOISELO=$400E
    .define NOISEHI=$400F
    .define DMCFREQ=$4010
    .define DMCRAW=$4011
    .define DMCSTART=$4012
    .define DMCLEN=$4013
    .define OAMDMA=$4014
    .define SNDCHNL=$4015
    .define CONTROL1=$4016
    .define CONTROL2=$4017
    .define FRAMECTRL=$4018
    .define PRGROM=$8000

