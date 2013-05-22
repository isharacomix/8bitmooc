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
    return 0x4000 - rom[0x10:0x4004].count(0xff)


# Test autograded assignment.
def test(challenge, student, code, completed):
    return "You always pass this assignment"


def barcamp1(challenge, student, code, completed):
    a = Assembler()
    rom, errors = a.assemble( ".org $C000\n"+code + "\nforever:\n jmp forever\n.org $fffa\n.dw $C000\n.dw $C000\n.dw $C000" )
    if errors: return None
    
    e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
    for i in range(0x100):
        e.step()
        if e.last_op == 0x60: break
    if e.X == 160 and e.Y == 100:
        return rom_size(rom), 100
    else: None
    
def barcamp2(challenge, student, code, completed):
    a = Assembler()
    
    preamble = ".org $C000\n.define BALL_X=$200\n.define BALL_Y=$201\n.define BALL_DX=$202\n.define BALL_DY=$203\n"
    postamble = "\nforever:\n jmp forever\n.org $fffa\n.dw $C000\n.dw $C000\n.dw $C000"
    
    rom, errors = a.assemble( preamble+code + postamble )
    if errors: return None
    for test in [[54,32,1,1],[0,99,0xff,0xff],[55,0xff,0xff,1]]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        e.write( test[0], 0x200 )
        e.write( test[1], 0x201 )
        e.X = test[2]
        e.Y = test[3]
        for i in range(0x100):
            e.step()
            if e.last_op == 0x60: break
        if e.read(0x200) != (test[0]+test[2])&0xff or e.read(0x201) != (test[1]+test[3])&0xff:
            return None
    return rom_size(rom), 100

def barcamp3(challenge, student, code, completed):
    a = Assembler()
    
    preamble = ".org $C000\n.define PADDLE_1Y=$204\n"
    postamble = "\nforever:\n jmp forever\n.org $fffa\n.dw $C000\n.dw $C000\n.dw $C000"
    
    rom, errors = a.assemble( preamble+code + postamble )
    if errors: None
    for test in [[0],[4],[5],[4,3]]:
        e = Emulator( rom[0x10:0x4010], rom[0x4010:] )
        for t in test: e.controller(1,t)
        for i in range(0x100):
            e.step()
            if e.last_op == 0x60: break
        if 4 in test and e.read(0x204) != 1: return None
        if 5 in test and e.read(0x204) != 0xff: return None
    return rom_size(rom), 100


# This function actually runs the autograder, mapping strings to functions.
# It essentially returns True if the assignment was successful, and it also
# does a bunch of side effects when successful as well.
# TODO: Be sure to collect runtime stats and compile length.
def grade(challenge, student, code, completed):
    AUTOGRADE_FUNCTIONS = {
                            "test": test,
                            "barcamp1": barcamp1,
                            "barcamp2": barcamp2,
                            "barcamp3": barcamp3,
                          }
    if challenge.autograde in AUTOGRADE_FUNCTIONS:
        func = AUTOGRADE_FUNCTIONS[challenge.autograde]
        return func(challenge, student, code, completed)
    else:
        return None


    
