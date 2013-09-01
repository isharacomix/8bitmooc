# -*- coding: utf-8 -*-

# This file does the autograding for 8bitmooc. Each function is associated with
# a challenge. These challenges evaluate a student subroutine using a series of
# tests and, if it runs correctly, returns a tuple containing the length of the
# program and the number of steps it took to run it.

from django.core import exceptions

from nes.models import Pattern
from nes.assembler import Assembler
from nes.emulator import Emulator

import time
import random

# The length of the ROM is determined by removing all of the dummy characters
# (0xFF) from the ROM and then counting what's left.
def rom_size( rom ):
    return 0x4000 - rom[0x10:0x4010].count('\xff')


# This runs the emulation and returns how long it takes before the RTS
# instruction is run. The emulation stops early if the limit is reached.
def run( emu, limit ):
    i = 0
    emu.last_op = None
    while i < limit and emu.last_op != 0x60:
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
    .define FRAMECTRL=$4017
    .define PRGROM=$8000"""


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
    
    counts = []
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
        counts.append( run( e, 0x100 ) )
        if e.read(0x200) != x or e.read(0x201) != y:
            return None
    return rom_size(rom), sum(counts)/len(counts)


# Challenge 1-2: Rendering Text
def easy2(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( """%s
                              .org $C000
                              .define TEXT=$E000
                              %s
                              forever: jmp forever
                              .org $fffa
                              .dw $C000
                              .dw $C000
                              .dw $C000
                              """%(memmap, code) )
    if errors: return None
    
    rom = rom[:0x2010]+("\xff"*0x500)+rom[0x2510:]

    counts = []
    for test in ["Hello world","Potato skillets"]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        for i,c in enumerate(test):
            e.rom[0x6000+i] = ord(c)
        counts.append( run( e, 0x10000 ) )
        for i,c in enumerate(test):
            print e.vram[0x2020+i]
        for i,c in enumerate(test):
            if e.vram[0x2020+i] != ord(c):
                return None
    return rom_size(rom), sum(counts)/len(counts)
    

# Challenge 1-3: Sprites and OAM.
def easy3(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( """%s
                              .org $C000
                              .define PLAYER1X=$200
                              .define PLAYER1Y=$201
                              .define PLAYER2X=$202
                              .define PLAYER2Y=$203
                              .define BALLX=$204
                              .define BALLY=$205
                              %s
                              forever: jmp forever
                              .org $fffa
                              .dw $C000
                              .dw $C000
                              .dw $C000
                              """%(memmap, code) )
    if errors: return None

    counts = []
    for test in [[41,61,11,13,9,14],[61,11,13,9,14,99]]:
        p1x,p1y,p2x,p2y,bx,by = test
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        i = 0
        while i < 6:
            e.write( test[i], 0x200+i )
            i += 1
        counts.append( run( e, 0x200 ) )
        if e.oam[0:4] != [0,0x20,0,0]: return None
        if e.oam[4:8] != [p1y,0x20,1,p1x]: return None
        if e.oam[8:12] != [p1y+8,0x20,1,p1x]: return None
        if e.oam[12:16] != [p1y+16,0x20,1,p1x]: return None
        if e.oam[16:20] != [by,0x20,0,bx]: return None
        if e.oam[20:24] != [p2y,0x20,2,p2x]: return None
        if e.oam[24:28] != [p2y+8,0x20,2,p2x]: return None
        if e.oam[28:32] != [p2y+16,0x20,2,p2x]: return None
        for a in e.oam[32:]:
            if a != 0: return None
    return rom_size(rom), sum(counts)/len(counts)



# Challenge 2-1: Sorting
def medium1(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( """%s
                              .org $C000
                              %s
                              forever: jmp forever
                              .org $fffa
                              .dw $C000
                              .dw $C000
                              .dw $C000
                              """%(memmap, code) )
    if errors: return None
    
    # Testing this one is easy. We simply create lists and then see if the
    # student's sort matches Python's. We will randomly create 5 lists to
    # average out "best cases". Granted, this means that it's possible for
    # a student to beat the "record" by just running the code multiple times,
    # but more efficient sorts should always win out.
    counts = []
    for test in range(5):
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        l = []
        for i in range(64): l.append(random.randint(0,255))
        for i in range(64): e.write( l[i], 0x200+i )
        
        counts.append( run( e, 0x10000 ) )
        l.sort()
        
        for i in range(64):
            if e.read( 0x200+i) != l[i]: return None
    
    return rom_size(rom), sum(counts)/len(counts)
    


# Challenge 3-1: Game of Life
def hard1(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( """%s
                              .org $C000
                              %s
                              forever: jmp forever
                              .org $fffa
                              .dw $C000
                              .dw $C000
                              .dw $C000
                              """%(memmap, code) )
    print errors
    if errors: return None
    

    
    # We do two basic tests. In the first, we simply start with a completely
    # filled grid. All cells should die.
    counts = []
    e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
    for i in range(0x100):
        e.write( 1, 0x200+i )
    counts.append( run( e, 0x100000 ) )
    for i in range(0x100):
        if e.read( 0x200+i ) != 0: return None
    
    # This is the real test. Note that we will actually run the program two times
    # to ensure that there are no side effects.
    start = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
              1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ]
    stage1= [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
              1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1 ]
    stage2= [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
              1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ]
    
    e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
    for i in range(0x100):
        e.write( start[i], 0x200+i )
    counts.append( run( e, 0x100000 ) )
    for i in range(0x100):
        if e.read( 0x200+i ) != stage1[i]: return None
    e.PC = 0xC000
    counts.append( run( e, 0x100000 ) )
    for i in range(0x100):
        if e.read( 0x200+i ) != stage2[i]: return None
    
    print "OK"
    return rom_size(rom), sum(counts)/len(counts)




# Challenge 3-3: Maze Solver
def hard3(challenge, student, code, completed):
    return None



# This function actually runs the autograder, mapping strings to functions.
# It essentially returns True if the assignment was successful, and it also
# does a bunch of side effects when successful as well.
def grade(challenge, student, code, completed):
    AUTOGRADE_FUNCTIONS = {
                            "easy1": easy1,
                            "easy2": easy2,
                            "easy3": easy3,
                            "medium1": medium1,
                            "hard1": hard1,
                            "hard3": hard3,
                          }
    if challenge.autograde in AUTOGRADE_FUNCTIONS:
        func = AUTOGRADE_FUNCTIONS[challenge.autograde]
        return func(challenge, student, code, completed)
    else:
        return None


    
