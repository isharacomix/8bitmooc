# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from students.models import Student

from assembler.asm import Assembler

# This test class tests the assembler's various functionalities. This isn't
# nearly as rigorous as actually verifying the output of an assembly program,
# but you know... baby steps.
class TestAssembler(TestCase):
    def setUp(self):
        self.A = Assembler()
    
    # When multiple lines are passed to the parser, they are broken into
    # four-tuples.
    def test_parse_lines(self):
        tokens = self.A.parse("""
            ; This line is a comment
            ; As is this one. All five lines should be completely empty.
            ; This one too lol
                              """)
        self.assertEquals( 5, len(tokens) )
        for l,o,a,orig in tokens:
            self.assertEquals( (a,b,c), (None,None,None))
    
    
    # When lines are passed to the parser, capital letters are made to lowercase
    def test_parse_labels(self):
        l,o,a,orig = self.A.parse("TeST: FoO; comment")[0]
        self.assertEquals( l, "test" )
        self.assertEquals( o, "foo" )
        self.assertEquals( a, None )
    
    
    # When lines are passed to the parser, whitespace is stripped from arguments
    def test_parse_lines(self):
        l,o,a,orig = self.A.parse("TEST:FOO     arg + arg   - 3 ; car")[0]
        self.assertEquals( l, "test" )
        self.assertEquals( o, "foo" )
        self.assertEquals( a, "arg+arg-3" )
    
    
    # When lines are passed to the parser, the original line is saved in the
    # fourth element of the tuple.
    def test_parse_lines(self):
        l,o,a,orig = self.A.parse("This is a   test; original")[0]
        self.assertEquals( l, None )
        self.assertEquals( o, "this" )
        self.assertEquals( a, "isatest" )
        self.assertEquals( orig, "(code) Line 1: This is a   test; original" )
    
    
    # This method tests all ten of the addressing modes based on the format of
    # the argument. For special cases, like LDX and STX, those are converted
    # internally.
    def test_addrmode(self):
        M_IMPLIED = 0
        M_REGISTER = 1
        M_IMMEDIATE = 2
        M_ZEROPAGE = 3
        M_ZEROPAGE_X = 4
        M_ABSOLUTE = 5
        M_ABSOLUTE_X = 6
        M_ABSOLUTE_Y = 7
        M_INDIRECT_X = 8
        M_INDIRECT_Y = 9
        
        # All of the following are legal constructs.
        self.assertEquals( self.A.addrmode(None), (M_IMPLIED, None) )
        self.assertEquals( self.A.addrmode(""), (M_IMPLIED, None) )
        self.assertEquals( self.A.addrmode("a"), (M_REGISTER, None) )
        self.assertEquals( self.A.addrmode("#label"), (M_IMMEDIATE, "label") )
        self.assertEquals( self.A.addrmode("#$42"), (M_IMMEDIATE, "$42") )
        self.assertEquals( self.A.addrmode("#$4242"), (M_IMMEDIATE, "$4242") )
        self.assertEquals( self.A.addrmode("$42"), (M_ZEROPAGE, "$42") )
        self.assertEquals( self.A.addrmode(">$4242"), (M_ZEROPAGE, ">$4242") )
        self.assertEquals( self.A.addrmode("-5"), (M_ZEROPAGE, "-5") )
        self.assertEquals( self.A.addrmode(">label"), (M_ZEROPAGE, ">label") )
        self.assertEquals( self.A.addrmode(">label,x"), (M_ZEROPAGE_X, ">label") )
        self.assertEquals( self.A.addrmode("label"), (M_ABSOLUTE, "label") )
        self.assertEquals( self.A.addrmode("$4242"), (M_ABSOLUTE, "$4242") )
        self.assertEquals( self.A.addrmode("$4242,x"), (M_ABSOLUTE_X, "$4242") )
        self.assertEquals( self.A.addrmode("$4242,y"), (M_ABSOLUTE_Y, "$4242") )
        self.assertEquals( self.A.addrmode("$42,y"), (M_ABSOLUTE_Y, "$42") )
        self.assertEquals( self.A.addrmode("($42,x)"), (M_INDIRECT_X, "$42") )
        self.assertEquals( self.A.addrmode("($42),y"), (M_INDIRECT_Y, "$42") )
        
        # This tests how some errors are taken care of - the addrmode function
        # does not complain, it simply pretends that the thing is a number and
        # tries to parse it.
        self.assertEquals( self.A.addrmode("($42,y)"), (M_ABSOLUTE, "($42,y)") )
    
    
    # This tests the number parsing system. Numbers support the most basic
    # arithmetic: addition and subtraction, and don't support anything fancy
    # like parens or multiplication.
    def test_nums(self):
        self.A.labels["test"] = 100
        self.A.labels["*"] = 42
        
        self.assertEquals( self.A.num("0x42"), 0x42 )
        self.assertEquals( self.A.num("0x42+0x42"), 0x84 )
        self.assertEquals( self.A.num("0x42+0x42+0x1"), 0x85 )
        self.assertEquals( self.A.num("0x42-0x42"), 0 )
        self.assertEquals( self.A.num("0x42-0x42+0x1"), 1 )
        self.assertEquals( self.A.num("-0x42"), 0xffbe ) #negative
        self.assertEquals( self.A.num("-test"), 0xff9c ) #negative
        self.assertEquals( self.A.num(">0x1234"), 0x34 )
        self.assertEquals( self.A.num("<0x1234"), 0x12 )
        self.assertEquals( self.A.num("test+*"), 142 )
    
    
    # This tests parsing hex, binary, octal, and decimal numbers.
    def test_parsenum(self):
        self.A.labels["test"] = 100
        self.A.labels["*"] = 42
        
        self.assertEquals( self.A.parsenum("0x42"), 0x42 )
        self.assertEquals( self.A.parsenum("$42"), 0x42 )
        self.assertEquals( self.A.parsenum("042"), 042 )
        self.assertEquals( self.A.parsenum("@42"), 042 )
        self.assertEquals( self.A.parsenum("42"), 42 )
        self.assertEquals( self.A.parsenum("0b1001"), 0b1001 )
        self.assertEquals( self.A.parsenum("%1001"), 0b1001 )
        self.assertEquals( self.A.parsenum("test"), 100 )
        self.assertEquals( self.A.parsenum("*"), 42 )
        self.assertEquals( self.A.parsenum("fake"), 0 )
        self.assertEquals( self.A.errors[0], "[Unknown label: 'fake'] ")
        
