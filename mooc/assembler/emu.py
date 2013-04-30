# -*- coding: utf-8 -*-

# My NES Emulator. It's not perfect, and doesn't really utilize any sort of
# audio/visual elements, but focuses on the register values of the hardware.

class Emulator(object):
    def __init__(self, prgrom, chrrom):
        self.ram = [0x00]*0x800     # RAM, $800 worth, mapped from $0 to $2000
        self.rom = [0x00]*0x8000    # ROM, $8000 worth in two banks. students
                                    # usually only use from $C000-$FFFF.
        self.sram = [0x00]*0x2000   # Battery backed RAM, from $6000-$8000.
        self.vram = [0x00]*0x4000   # PPU RAM
        self.oam = [0x00]*4*64
        
        # CPU Registers
        self.A = 0x00               # Accumulator
        self.X = 0x00               # X Index
        self.Y = 0x00               # Y Index
        self.SP = 0x00              # Stack pointer
        self.PC = 0x00              # Program counter
        self.status = 0x00          # Status register
        

    
    # This writes a byte to memory, handling mirroring and all that nonsense.
    def write(self, what, where):
        what, where = what&0xff, where&0xffff
        if   where >= 0x8000: pass
        elif where >= 0x6000: self.sram[where-0x6000] = what
        elif where >= 0x4020: pass
        elif where >= 0x4000: write_apu( what, where-0x4000 )
        elif where >= 0x2000: write_ppu( what, where % 0x8 )
        else: self.ram[ where % 0x800 ] = what
    
    # These reads a byte from memory, handling mirroring and all that nonsense.
    def read(self, where):
        where = where&0xffff
        if   where >= 0x8000: return self.rom[where-0x8000]
        elif where >= 0x6000: return self.sram[where-0x6000]
        elif where >= 0x4020: return 0x00
        elif where >= 0x4000: return read_apu( where-0x4000 )
        elif where >= 0x2000: return read_ppu( where % 0x8 )
        else: return self.ram[ where % 0x800 ]

    # This steps through one instruction. It returns something TODO
    def step(self):
        pass

