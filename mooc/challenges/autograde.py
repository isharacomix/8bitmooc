# -*- coding: utf-8 -*-

# This file does the autograding for 8bitmooc. Each function is associated with
# a challenge. These challenges evaluate a student subroutine using a series of
# tests and, if it runs correctly, returns a tuple containing the length of the
# program and the number of steps it took to run it.

from django.core import exceptions

from nes.models import Pattern
from nes.assembler import Assembler
from nes.emulator import Emulator


# The length of the ROM is determined by removing all of the dummy characters
# (0xFF) from the ROM and then counting what's left.
def rom_size( rom ):
    return 0x4000 - rom[0x10:0x4010].count('\xff')


# This runs the emulation and returns how long it takes before the RTS
# instruction is run. The emulation stops early if the limit is reached.
def run( emu, limit ):
    i = 0
    while i < limit and emu.last_op != 0x60:
        #print emu.decode(emu.last_op),hex(emu.last_addr) if emu.last_addr else "-"
        emu.step()
        i += 1
    return i


memmap = """.define ZEROPAGE=$0000
    .define STACK=$0100
    .define PPUCTRL=$2000
    .define PPUMASK=$2001
    .define PPUSTATUS=$2002
    .define OAMADDR=$2003
    .define OAMDATA=$2004
    .define SCROLL=$2005
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
    .define PRGROM=$8000"""


# Test autograded assignment.
def test(challenge, student, code, completed):
    return 100, 100

# Challenge 1-1: Tests the controller input.
def easy1(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( """%s
                              .org $C000
                              .define PLAYER_X=$200
                              .define PLAYER_Y=$201
                              %s
                              forever: jmp forever
                              .org $fffa
                              .dw $C000
                              .dw $C000
                              .dw $C000
                              """%(memmap, code) )
    if errors: return None
    
    count = 0
    for test in [[0],[1],[2],[3],[4],[5],[6],[7],[4,5],[4,6],[4,7],[5,7],[4,5,6,7]]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        x = 74
        y = 32
        e.write(x,0x200)
        e.write(y,0x201)
        for t in test:
            e.controller(1, t)
        if 4 in test: y-=1
        if 5 in test: y+=1
        if 6 in test: x-=1
        if 7 in test: x+=1
        count += run( e, 0x100 )
        if e.read(0x200) != x and e.read(0x201) != y:
            return None
    return rom_size(rom), count




def barcamp2(challenge, student, code, completed):
    a = Assembler()
   
    preamble = ".org $C000\n.define BALL_X=$200\n.define BALL_Y=$201\n.define BALL_DX=$202\n.define BALL_DY=$203\n"
    postamble = "\nforever:\n jmp forever\n.org $fffa\n.dw $C000\n.dw $C000\n.dw $C000"
    
    rom, errors = a.assemble( preamble+code + postamble )
    if errors: return None
    counts = []
    for test in [[54,32,1,1],[0,99,0xff,0xff],[55,0xff,0xff,1]]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        e.write( test[0], 0x200 )
        e.write( test[1], 0x201 )
        e.X = test[2]
        e.Y = test[3]
        counts.append( run( e, 0x100 ) )
        if e.read(0x200) != (test[0]+test[2])&0xff or e.read(0x201) != (test[1]+test[3])&0xff:
            return None
    return rom_size(rom), sum(counts)

def barcamp3(challenge, student, code, completed):
    a = Assembler()
    
    preamble = ".org $C000\n.define PADDLE_1Y=$204\n"
    postamble = "\nforever:\n jmp forever\n.org $fffa\n.dw $C000\n.dw $C000\n.dw $C000"
    
    rom, errors = a.assemble( preamble+code + postamble )
    if errors: None
    counts = []
    for test in [[0],[4],[5],[4,3]]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        for t in test: e.controller(1,t)
        counts.append( run( e, 0x100 ) )
        if 4 in test and e.read(0x204) != 1: return None
        if 5 in test and e.read(0x204) != 0xff: return None
    return rom_size(rom), sum(counts)


# This function actually runs the autograder, mapping strings to functions.
# It essentially returns True if the assignment was successful, and it also
# does a bunch of side effects when successful as well.
def grade(challenge, student, code, completed):
    AUTOGRADE_FUNCTIONS = {
                            "test": test,
                            "barcamp2": barcamp2,
                            "barcamp3": barcamp3,
                            "easy1": easy1,
                          }
    if challenge.autograde in AUTOGRADE_FUNCTIONS:
        func = AUTOGRADE_FUNCTIONS[challenge.autograde]
        return func(challenge, student, code, completed)
    else:
        return None


    
