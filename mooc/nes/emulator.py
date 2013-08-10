# -*- coding: utf-8 -*-

# My NES Emulator. It's not perfect, and doesn't really utilize any sort of
# audio/visual elements, but focuses on the register values of the hardware.

# This emulator exists in order to allow 8bitmooc to autograde assignments.
# To grade an assignment, create the emulator and pass the student's PRG and
# CHR ROM. Then, in a loop, run the step command. If you are trying to simulate
# gameplay and intend to draw frames, NMIs are fired every 10000 steps.

# The .read and .write methods handle the hardware register magic. When grading,
# use the variables set forth in the initializer. It's suggested to read the raw
# arrays instead when looking at RAM and such.

BUTTON_A = 0
BUTTON_B = 1
BUTTON_START = 2
BUTTON_SELECT = 3
BUTTON_UP = 4
BUTTON_DOWN = 5
BUTTON_LEFT = 6
BUTTON_RIGHT = 7
BUTTON_ALL = 8

# To instantiate the emulator, create it with PRG and CHR rom arrays as its
# arguments. These will be loaded into the rom and vram, respectively.
class Emulator(object):
    def __init__(self, prgrom=None, chrrom=None):
        self.ram = [0x00]*0x800     # RAM, $800 worth, mapped from $0 to $2000
        self.rom = [0x00]*0x8000    # ROM, $8000 worth in two banks. students
                                    # usually only use from $C000-$FFFF.
        self.sram = [0x00]*0x2000   # Battery backed RAM, from $6000-$8000.
        self.vram = [0x00]*0x4000   # PPU RAM
        self.oam = [0x00]*4*64      # OAM (sprite data)
        self.vram_mirror = 3        # 0 all mirror, 1 vert, 2 horiz, 3 unique
        
        self.debug = []
        self.last_op = None
        self.last_mode = None
        self.last_arg = None
        self.last_addr = None
        
        # vblank interval can be reprogrammed if needed
        self.vblank_interval = 10000
        self.next_vblank = self.vblank_interval
        
        # CPU Registers
        self.A = 0x00               # Accumulator
        self.X = 0x00               # X Index
        self.Y = 0x00               # Y Index
        self.SP = 0x00              # Stack pointer
        self.PC = 0x00              # Program counter
        self.N = False              # Status Register Flags
        self.V = False
        self.B = False
        self.D = False
        self.I = False
        self.Z = False
        self.C = False
        
        # Controllers
        self.p1 = 0x00              # Physical controller state
        self.p2 = 0x00              #
        self.internal_p1 = 0x00     # Internal controller state
        self.internal_p2 = 0x00     #
        
        # Sound timers
        self.square1_t = 0x00       # The number of clock cycles left
        self.square2_t = 0x00       # in each channel before the note ends
        self.triangle_t = 0x00      # 
        self.noise_t = 0x00         #
        self.dmc_t = 0x00           #
        self.apu_regs = [0x00]*0x14 # The registers for the APU.
        
        # PPU Registers
        self.base_nametable = 0     # Which table? $2000 + this * $400
        self.ppu_increment = 0      # Increment by 1 (across) or 32 (down)?
        self.sprite_table = 0       # Which table is the sprites?
        self.bg_table = 0           # Which table is the background?
        self.big_sprites = False    # Sprites are 8x16 when true
        self.vblank_nmi = False     # When True, we fire an NMI every 60 frames
        
        self.grayscale = False
        self.show_leftbg = False
        self.show_leftsprites = False
        self.show_bg = False
        self.show_sprites = False
        self.red = False
        self.green = False
        self.blue = False
        self.oam_addr = 0
        self.ppu_addr = 0            # The only one that is 16-bit
        self.scroll_x = 0
        self.scroll_y = 0
        self.vblank = 0
        
        # Semaphores for $2005-$2007. Read from PPUStatus to reset the latch
        self.scroll_sem = 0         # When 0, we write to X
        self.address_sem = 0        # When 0, we write to the upper byte
        
        # Load the ROM and VRAM with our arguments.
        if prgrom and len(prgrom)<=0x8000:
            for i in range(0,len(prgrom)):
                self.rom[-1-i] = ord(prgrom[-1-i])&0xff
        if chrrom and len(chrrom)==0x2000:
            for i in range(0,0x2000):
                self.vram[i] = ord(chrrom[i])&0xff
        self.PC = self.read(0xFFFC) | (self.read(0xFFFD)<<8)
        self.I = True
    
    # Returns the status byte using the processor flags.
    def status(self):
        x = 0
        x |= 0x80 if self.N else 0
        x |= 0x40 if self.V else 0
        x |= 0x20
        x |= 0x10 if self.B else 0
        x |= 0x08 if self.D else 0
        x |= 0x04 if self.I else 0
        x |= 0x02 if self.Z else 0
        x |= 0x01 if self.C else 0
        return x
    
    # Sets the status flags equal to the correct bits.
    def read_status(self, byte):
        self.N = ((byte & 0x80) > 0)
        self.V = ((byte & 0x40) > 0)
        self.B = ((byte & 0x10) > 0)
        self.D = ((byte & 0x08) > 0)
        self.I = ((byte & 0x04) > 0)
        self.Z = ((byte & 0x02) > 0)
        self.C = ((byte & 0x01) > 0)
    
    # This sets the N and Z flag based on an input byte.
    def flagify(self, byte):
        self.N = ((byte & 0x80) > 0)
        self.Z = (byte == 0)
    
    # This writes a variable to the stack page (0x100-0x1FF) and decrements the
    # stack pointer (SP).
    def push(self, what):
        self.write( what, 0x100 | self.SP )
        self.SP = (self.SP-1)&0xFF
    
    # This pulls a variable from the stack page (0x100-0x1FF) and increments the
    # stack pointer.
    def pull(self):
        self.SP = (self.SP+1)&0xFF
        return self.read( 0x100 | self.SP )
    
    # Returns a mapped vram address
    def vram_addr(self, where):
        where &= 0x4000
        if where >= 0x3F00:
            return ((where-0x3F00)%0x20) + 0x3F00
        if where >= 0x3000: where -= 0x1000
        return where
    
    # This writes to the PPU. Legal "where" values include 0x00-0x07
    def write_ppu(self, what, where):
        if where == 0x00:
            self.base_nametable = what & 0x3
            self.ppu_increment = 1 if (what & 0x4) == 0 else 32
            self.sprite_table = 0 if (what & 0x8) == 0 else 1
            self.bg_table = 0 if (what & 0x10) == 0 else 1
            self.big_sprites = False if (what & 0x20) == 0 else True
            self.vblank_nmi = False if (what & 0x80) == 0 else True
        if where == 0x01:
            self.grayscale = False if (what & 0x1) == 0 else True
            self.show_leftbg = False if (what & 0x2) == 0 else True
            self.show_leftsprites = False if (what & 0x4) == 0 else True
            self.show_bg = False if (what & 0x8) == 0 else True
            self.show_sprites = False if (what & 0x10) == 0 else True
            self.red = False if (what & 0x20) == 0 else True
            self.green = False if (what & 0x40) == 0 else True
            self.blue = False if (what & 0x80) == 0 else True
        if where == 0x03:
            self.oam_addr = what
        if where == 0x04:
            self.oam[self.oam_addr] = what
            self.oam_addr += 1
        if where == 0x05:
            if self.scroll_sem == 0: self.scroll_x = what
            if self.scroll_sem == 1: self.scroll_y = what
            self.scroll_sem += 1
        if where == 0x06:
            if self.address_sem == 0:
                self.ppu_addr &= 0xff
                self.ppu_addr |= (what << 8)
            if self.address_sem == 1:
                self.ppu_addr &= 0xff00
                self.ppu_addr |= what
            self.address_sem += 1
        if where == 0x07:
            self.vram[self.vram_addr(self.ppu_address)] = what
            self.ppu_address += self.ppu_increment

    
    # This reads from the PPU. Legal "where" values inclide 0x00-0x07, but 
    # really only one value is meaningful. We follow theoretical optimism, and
    # allow you to read from the OAM and VRAM registers.
    def read_ppu(self, where):
        if where == 0x02:
            x = 0
            if self.vblank: x |= 0x80
            self.vblank = 0
            self.scroll_sem = 0
            self.address_sem = 0
            return x
        if where == 0x04:
            return self.oam[self.oam_addr]
        if where == 0x07:
            return self.vram[self.vram_addr(self.ppu_address)]
        return 0x00
    
    
    # This writes to the APU (which also includes the controllers).
    # Legal "where" values include 0x00-0x1F
    def write_apu(self, what, where):
        if where == 0x14: #OAM
            for i in range(0x100):
                b = self.read( what<<8 | i )
                self.oam[self.oam_addr] = b
                self.oam_addr = (self.oam_addr+1)&0xff
        if where == 0x16:
            if what&1 == 1:
                self.internal_p1 = self.p1
                self.internal_p2 = self.p2
            if what&0 == 1:
                self.p1 = 0
                self.p2 = 0
        if where == 0x17: #Frame counter
            pass #TODO
        if where < 0x14:
            self.apu_regs[where] = what
        # TODO the values under $14 are for the various instruments. This will
        # affect the timers, but isn't a super big deal atm.
    
    # This reads from the APU - which only includes four registers:
    # Legal "where" values include 0x00-0x1F
    def read_apu(self, where):
        if where == 0x15:
            x = 0
            if self.square1_t > 0: x |= 0x01
            if self.square2_t > 0: x |= 0x02
            if self.triangle_t > 0: x |= 0x04
            if self.noise_t > 0: x |= 0x08
            if self.dmc_t > 0: x |= 0x10
            # bit 1 needs to be equal to frame interrupt
            # bit 0 needs to be equal to DMC interrupt
            return x
        if where == 0x16:
            x = self.internal_p1 & 1
            self.internal_p1 >>= 1
            return x
        if where == 0x17:
            x = self.internal_p2 & 1
            self.internal_p2 >>= 1
            return x
        return 0x00
    
    
    # This writes a byte to memory, handling mirroring and all that nonsense.
    def write(self, what, where):
        what &= 0xff
        where &= 0xffff
        if   where >= 0x8000: pass
        elif where >= 0x6000: self.sram[where-0x6000] = what
        elif where >= 0x4020: pass
        elif where >= 0x4000: self.write_apu( what, where-0x4000 )
        elif where >= 0x2000: self.write_ppu( what, where % 0x8 )
        else: self.ram[ where % 0x800 ] = what
    
    # These reads a byte from memory, handling mirroring and all that nonsense.
    def read(self, where):
        where &= 0xffff
        if   where >= 0x8000: return self.rom[where-0x8000]
        elif where >= 0x6000: return self.sram[where-0x6000]
        elif where >= 0x4020: return 0x00
        elif where >= 0x4000: return self.read_apu( where-0x4000 )
        elif where >= 0x2000: return self.read_ppu( where % 0x8 )
        else: return self.ram[ where % 0x800 ]
    
    # This reads a WORD from memory. If page wrap is true, then when the low
    # byte is at the end of a page $xxFF, the high byte comes from the beginning
    # of that page $xx00.
    def read_word(self, where, page_wrap=False):
        if page_wrap:
            where_hi = (where >> 8)&0xff
            where_lo = where & 0xff
            lo = self.read( where )
            hi = self.read( where_hi | (where_lo+1)&0xFF)
            return lo | (hi << 8 )
        else:
            lo = self.read( where )
            hi = self.read( where+1 )
            return lo | (hi << 8)
    
    # This reads from the program counter and increments it.
    def read_PC(self):
        x = self.read(self.PC)
        self.PC = (self.PC+1)&0xFFFF
        return x
    def read_word_PC(self):
        x = self.read_word(self.PC)
        self.PC = (self.PC+2)&0xFFFF
        return x
    
    # This handles getting the argument from a full addressing mode operation.
    def get_argmode(self, op, IMM, ZPAGE, ZPAGEX, ABS, ABSX, ABSY, INDX, INDY):
        arg = None
        addr = None
        if op in [IMM, ZPAGE, ZPAGEX, INDX, INDY]:
            addr = self.read_PC()
            if op == IMM: arg = addr
            if op == ZPAGEX or op == INDX: addr = (addr+self.X)&0xFF
            if op == INDX or op == INDY: addr = self.read_word(addr, True)
            if op == INDY: addr = (addr+self.Y)&0xFFFF
            if op != IMM: arg = self.read(addr)
        else:
            addr = self.read_word_PC()
            if op == ABSX: addr = (addr+self.X)&0xFFFF
            if op == ABSY: addr = (addr+self.Y)&0xFFFF
            arg = self.read(addr)
        self.last_addr = addr
        self.last_arg = arg
        return arg
    
    
    # The actual emulation. We emulate at the instruction level, not the clock
    # level, which makes it easier, but less accurate.
    def next_instruction(self):
        self.last_op = None
        self.last_mode = None
        self.last_arg = None
        self.last_addr = None
        op = self.read_PC()
        self.last_op = op
        
        if op in [0x69, 0x65, 0x75, 0x6D, 0x7D, 0x79, 0x61, 0x71]: #ADC
            arg = self.get_argmode(op,0x69,0x65,0x75,0x6D,0x7D,0x79,0x61,0x71)
            result = (self.A + arg + (1 if self.C else 0))
            self.C = result > 0xFF
            self.V = ((self.A & 0x80 > 0 and arg & 0x80 > 0 and (not self.C)) or
                      (self.A & 0x80 <=0 and arg & 0x80 <=0 and (self.C)))
            self.A = result&0xFF
            self.flagify(self.A)
        elif op in [0x29, 0x25, 0x35, 0x2D, 0x3D, 0x39, 0x21, 0x31]: #AND
            arg = self.get_argmode(op,0x29,0x25,0x35,0x2D,0x3D,0x39,0x21,0x31)
            result = (self.A & arg)
            self.A = result
            self.flagify(self.A)
        elif op in [0x0A, 0x06, 0x16, 0x0E, 0x1E]: #ASL
            if op == 0x0A:
                self.A <<= 1
                self.C = self.A > 0xFF
                self.A &= 0xFF
                self.flagify(self.A)
            else:
                addr = None
                if op in [0x06, 0x16]:
                    addr = self.read_PC()
                    if addr == 0x16: addr = (addr+self.X)&0xFF
                else:
                    addr = self.read_word_PC()
                    if addr == 0x1E: addr = (addr+self.X)&0xFFFF
                result = self.read(addr) << 1
                self.C = result > 0xFF
                result &= 0xFF
                self.flagify(result)
                self.write(result, addr)
        elif op in [0x24, 0x2C]: #BIT
            addr = None
            if addr == 0x24: addr = self.read_PC()
            if addr == 0x2C: addr = self.read_word_PC()
            arg = self.read(addr)
            self.Z = (arg == self.A)
            self.N = ((arg & 0x80) > 0)
            self.V = ((arg & 0x40) > 0)
        elif op in [0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0]: #Branch
            do_branch = False
            offset = self.read_PC()
            if op == 0x10: do_branch = not self.N
            elif op == 0x30: do_branch = self.N
            elif op == 0x50: do_branch = not self.V
            elif op == 0x70: do_branch = self.V
            elif op == 0x90: do_branch = not self.C
            elif op == 0xB0: do_branch = self.C
            elif op == 0xD0: do_branch = not self.Z
            elif op == 0xF0: do_branch = self.Z
            if do_branch:
                if (offset & 0x80) > 0:
                    offset += -0x100
                self.PC = (self.PC+offset)&0xFFFF
        elif op == 0x00: #BRK
            self.PC = (self.PC+1)&0xFFFF
            self.send_irq()
        elif op in [0xC9, 0xC5, 0xD5, 0xCD, 0xDD, 0xD9, 0xC1, 0xD1]: #CMP
            arg = self.get_argmode(op,0xC9,0xC5,0xD5,0xCD,0xDD,0xD9,0xC1,0xD1)
            self.Z = (self.A == arg)
            self.S = ((self.A & 0x80) > 0)
            self.C = (self.A >= arg)
        elif op in [0xE0, 0xE4, 0xEC]: #CPX
            arg = None
            if op == 0xE0: arg = self.read_PC()
            if op == 0xE4: arg = self.read(self.read_PC())
            if op == 0xEC: arg = self.read(self.read_word_PC())
            self.Z = (self.X == arg)
            self.S = ((self.X & 0x80) > 0)
            self.C = (self.X >= arg)
        elif op in [0xC0, 0xC4, 0xCC]: #CPY
            arg = None
            if op == 0xC0: arg = self.read_PC()
            if op == 0xC4: arg = self.read(self.read_PC())
            if op == 0xCC: arg = self.read(self.read_word_PC())
            self.Z = (self.Y == arg)
            self.S = ((self.Y & 0x80) > 0)
            self.C = (self.Y >= arg)
        elif op in [0xC6, 0xD6, 0xCE, 0xDE]: #DEC
            addr = None
            if op in [0xC6, 0xD6]:
                addr = self.read_PC()
                if addr == 0xD6: addr = (addr+self.X)&0xFF
            else:
                addr = self.read_word_PC()
                if addr == 0xDE: addr = (addr+self.X)&0xFFFF
            result = (self.read(addr) - 1)&0xFF
            self.flagify(result)
            self.write(result, addr)
        elif op in [0x49, 0x45, 0x55, 0x4D, 0x5D, 0xD9, 0x41, 0x51]: # EOR
            arg = self.get_argmode(op,0x49,0x45,0x55,0x4D,0x5D,0xD9,0x41,0x51)
            result = (self.A ^ arg)
            self.A = result
            self.flagify(self.A)
        elif op == 0x18: self.C = False #CLC
        elif op == 0x38: self.C = True #SEC
        elif op == 0x58: self.I = False #CLI
        elif op == 0x78: self.I = True #SEI
        elif op == 0xB8: self.V = False #CLV 
        elif op == 0xD8: self.D = False #CLD
        elif op == 0xF8: self.D = True #SED
        elif op in [0xE6, 0xF6, 0xEE, 0xFE]: #INC
            addr = None
            if op in [0xE6, 0xF6]:
                addr = self.read_PC()
                if addr == 0xF6: addr = (addr+self.X)&0xFF
            else:
                addr = self.read_word_PC()
                if addr == 0xFE: addr = (addr+self.X)&0xFFFF
            result = (self.read(addr) + 1)&0xFF
            self.flagify(result)
            self.write(result, addr)
        elif op in [0x4C, 0x6C, 0x20]: #JMP/JSR
            if op == 0x4C:
                self.PC = self.read_word( self.PC )
            elif op == 0x6C:
                addr = self.read_word( self.PC )
                self.PC = self.read_word( addr, True )
            elif op == 0x20:
                addr = self.read_word( self.PC )
                self.PC = (self.PC+1)&0xFFFF
                self.push( (self.PC >> 8)&0xFF )
                self.push( (self.PC)&0xFF )
                self.PC = addr
        elif op in [0xA9, 0xA5, 0xB5, 0xAD, 0xBD, 0xB9, 0xA1, 0xB1]: #LDA
            self.A = self.get_argmode(op,0xA9,0xA5,0xB5,0xAD,0xBD,0xB9,0xA1,0xB1)
            self.flagify(self.A)
        elif op in [0xA2, 0xA6, 0xB6, 0xAE, 0xBE]: #LDX
            arg = None
            if op in [0xA2, 0xA6, 0xB6]:
                addr = self.read_PC()
                if op == 0xA2: arg = addr
                if op == 0xB6: addr = (addr+self.Y)&0xFF
                if op != 0xA2: arg = self.read(addr)
            else:
                addr = self.read_word_PC()
                if op == 0xBE: addr = (addr+self.Y)&0xFFFF
                arg = self.read(addr)
            self.X = arg
            self.flagify(self.X)
        elif op in [0xA0, 0xA4, 0xB4, 0xAC, 0xBC]: #LDY
            arg = None
            if op in [0xA0, 0xA4, 0xB4]:
                addr = self.read_PC()
                if op == 0xA0: arg = addr
                if op == 0xB4: addr = (addr+self.X)&0xFF
                if op != 0xA0: arg = self.read(addr)
            else:
                addr = self.read_word_PC()
                if op == 0xBC: addr = (addr+self.X)&0xFFFF
                arg = self.read(addr)
            self.Y = arg
            self.flagify(self.Y)
        elif op in [0x4A, 0x46, 0x56, 0x4E, 0x5E]: #LSR
            if op == 0x4A:
                self.A <<= 1
                self.C = self.A > 0xFF
                self.A &= 0xFF
                self.flagify(self.A)
            else:
                addr = None
                if op in [0x46, 0x56]:
                    addr = self.read_PC()
                    if addr == 0x56: addr = (addr+self.X)&0xFF
                else:
                    addr = self.read_word_PC()
                    if addr == 0x5E: addr = (addr+self.X)&0xFFFF
                result = self.read(addr)
                self.C = ((result & 0x1)>0)
                result >>= 1
                self.flagify(result)
                self.write(result&0xFF, addr)
        elif op == 0xEA: pass #NOP
        elif op in [0x09, 0x05, 0x15, 0x0D, 0x1D, 0x19, 0x01, 0x11]: #ORA
            arg = self.get_argmode(op,0x09,0x05,0x15,0x0D,0x1D,0x19,0x01,0x11)
            result = (self.A | arg)
            self.A = result
            self.flagify(self.A)
        elif op == 0xAA: self.X = self.A          ; self.flagify(self.X) #TAX
        elif op == 0x8A: self.A = self.X          ; self.flagify(self.A) #TXA
        elif op == 0xCA: self.X = (self.X-1)&0xFF ; self.flagify(self.X) #DEX
        elif op == 0xE8: self.X = (self.X+1)&0xFF ; self.flagify(self.X) #INX
        elif op == 0xA8: self.Y = self.A          ; self.flagify(self.Y) #TAY
        elif op == 0x98: self.A = self.Y          ; self.flagify(self.A) #TYA
        elif op == 0x88: self.Y = (self.Y-1)&0xFF ; self.flagify(self.Y) #DEY
        elif op == 0xC8: self.Y = (self.Y+1)&0xFF ; self.flagify(self.Y) #INY
        elif op in [0x2A, 0x26, 0x36, 0x2E, 0x3E]: #ROL
            if op == 0x2A:
                self.A <<= 1
                self.C = self.A > 0xFF
                self.A &= 0xFF
                self.flagify(self.A)
            else:
                addr = None
                if op in [0x26, 0x36]:
                    addr = self.read_PC()
                    if addr == 0x36: addr = (addr+self.X)&0xFF
                else:
                    addr = self.read_word_PC()
                    if addr == 0x3E: addr = (addr+self.X)&0xFFFF
                result = (self.read(addr) << 1) | (1 if self.C else 0)
                self.C = result > 0xFF
                result &= 0xFF
                self.flagify(result)
                self.write(result, addr)
        elif op in [0x6A, 0x66, 0x76, 0x6E, 0x7E]: #ROR
            if op == 0x6A:
                self.A <<= 1
                self.C = self.A > 0xFF
                self.A &= 0xFF
                self.flagify(self.A)
            else:
                addr = None
                if op in [0x66, 0x76]:
                    addr = self.read_PC()
                    if addr == 0x76: addr = (addr+self.X)&0xFF
                else:
                    addr = self.read_word_PC()
                    if addr == 0x7E: addr = (addr+self.X)&0xFFFF
                result = self.read(addr) | (0x100 if self.C else 0)
                self.C = ((result & 0x1)>0)
                result >>= 1
                self.flagify(result)
                self.write(result&0xFF, addr)
        elif op in [0x40, 0x60]: #RTI/RTS
            if op == 0x40:
                self.read_status( self.pull() )
                lo = self.pull()
                hi = self.pull()
                self.PC = (lo | hi << 8)
            elif op == 0x60:
                lo = self.pull()
                hi = self.pull()
                self.PC = ((lo | hi << 8)+1)&0xFFFF
        elif op in [0xE9, 0xE5, 0xF5, 0xED, 0xFD, 0xF9, 0xE1, 0xF1]: #SBC
            arg = self.get_argmode(op,0xE9,0xE5,0xF5,0xED,0xFD,0xF9,0xE1,0xF1)
            result = ((self.A | (0x100 if self.C else 0) ) - arg - (0 if self.C else 1))
            self.C = result > 0xFF
            self.V = ((self.A & 0x80 > 0 and arg & 0x80 > 0 and (not self.C)) or
                      (self.A & 0x80 <=0 and arg & 0x80 <=0 and (self.C)))
            self.A = result&0xFF
            self.flagify(self.A)
        elif op in [0x85, 0x95, 0x8D, 0x9D, 0x99, 0x81, 0x91]: #STA
            addr = None
            if op in [0x85, 0x95, 0x81, 0x91]:
                addr = self.read_PC()
                if op == 0x95 or op == 0x81: addr = (addr+self.X)&0xFF
                if op == 0x81 or op == 0x91: addr = self.read_word(addr, True)
                if op == 0x91: addr = (addr+self.Y)&0xFFFF
            else:
                addr = self.read_word_PC()
                if op == 0x9D: addr = (addr+self.X)&0xFFFF
                if op == 0x99: addr = (addr+self.Y)&0xFFFF
            self.write( self.A, addr)
        elif op == 0x9A: self.SP = self.X #TXS
        elif op == 0xBA: self.X = self.SP; flagify(self.X) #TSX
        elif op == 0x48: self.push(self.A) #PHA
        elif op == 0x68: self.A = self.pull(); flagify(self.A) #PLA
        elif op == 0x08: self.push(self.status()) #PHS 
        elif op == 0x28: self.read_status( self.pull() ) #PLS
        elif op in [0x86, 0x96, 0x8E]: #STX
            addr = None
            if op == 0x8E:
                addr = self.read_word_PC()
            else:
                addr = self.read_PC()
                if op == 0x96: addr = (addr + self.Y)&0xFF
            self.write( self.X, addr )
        elif op in [0x84, 0x94, 0x8C]: #STY
            addr = None
            if op == 0x8C:
                addr = self.read_word_PC()
            else:
                addr = self.read_PC()
                if op == 0x94: addr = (addr + self.X)&0xFF
            self.write( self.Y, addr )
        else:
            return False
        
        return True
    
    # The three interrupts.
    def send_reset(self):
        self.PC = self.read(0xFFFC) | (self.read(0xFFFD)<<8)
        self.I = True
    def send_nmi(self):
        self.push( (self.PC >> 8)&0xFF )
        self.push( (self.PC)&0xFF )
        self.push( self.status() )
        self.PC = self.read(0xFFFA) | (self.read(0xFFFB)<<8)
        self.I = True
    def send_irq(self):
        self.push( (self.PC >> 8)&0xFF )
        self.push( (self.PC)&0xFF )
        self.push( self.status() )
        self.PC = self.read(0xFFFE) | (self.read(0xFFFF)<<8)
        self.I = True
    
    
    # These allow you to push buttons on a controller. When the controller is
    # strobed, the buttons will be released automatically.
    # A, B, Select, Start, Up, Down, Left, Right, All
    # 0, 1, 2,      3,     4,  5,    6,    7,     8
    # If 'press' is false, then it is released, not pressed.
    def controller(self, player, button, press=True):
        if press:
            k = (1 << button) if button != 8 else 0xff
            if player == 1: self.p1 |= k
            if player == 2: self.p2 |= k
        else:
            k = (0xff ^ (1 << button)) if button != 8 else 0x00
            if player == 1: self.p1 &= k
            if player == 2: self.p2 &= k


    # This steps through one instruction. Returns True if it was legal.
    def step(self):
        self.next_vblank -= 1
        if self.next_vblank <= 0:
            self.next_vblank = self.vblank_interval
            self.vblank = True
            if self.vblank_nmi:
                self.send_nmi()
        
        # read the next instruction and run it
        self.next_instruction()
    
    # This decodes an operation.
    def decode(self, opcode):
        if opcode in [0x69,0x65,0x75,0x6D,0x7D,0x79,0x61,0x71]: return "adc"
        if opcode in [0x29,0x25,0x35,0x2D,0x3D,0x39,0x21,0x31]: return "and"
        if opcode in [0x0A,0x06,0x16,0x0E,0x1E]: return "asl"
        if opcode in [0x24,0x2C]: return "bit"
        if opcode in [0x10]: return "bpl"
        if opcode in [0x30]: return "bmi"
        if opcode in [0x50]: return "bvc"
        if opcode in [0x70]: return "bvs"
        if opcode in [0x90]: return "bcc"
        if opcode in [0xB0]: return "bcs"
        if opcode in [0xD0]: return "bne"
        if opcode in [0xF0]: return "beq"
        if opcode in [0x00]: return "brk"
        if opcode in [0xC9,0xC5,0xD5,0xCD,0xDD,0xD9,0xC1,0xD1]: return "cmp"
        if opcode in [0xE0,0xE4,0xEC]: return "cpx"
        if opcode in [0xC0,0xC4,0xCC]: return "cpy"
        if opcode in [0xC6,0xD6,0xCE,0xDE]: return "dec"
        if opcode in [0x49,0x45,0x55,0x4D,0x5D,0x59,0x41,0x51]: return "eor"
        if opcode in [0x18]: return "clc"
        if opcode in [0x38]: return "sec"
        if opcode in [0x58]: return "cli"
        if opcode in [0x78]: return "sei"
        if opcode in [0xB8]: return "clv"
        if opcode in [0xD8]: return "cld"
        if opcode in [0xF8]: return "sed"
        if opcode in [0xE6,0xF6,0xEE,0xFE]: return "inc"
        if opcode in [0x4C,0x6C]: return "jmp"
        if opcode in [0x20]: return "jsr"
        if opcode in [0xA9,0xA5,0xB5,0xAD,0xBD,0xB9,0xA1,0xB1]: return "lda"
        if opcode in [0xA2,0xA6,0xB6,0xAE,0xBE]: return "ldx"
        if opcode in [0xA0,0xA4,0xB4,0xAC,0xBC]: return "ldy"
        if opcode in [0x4A,0x46,0x56,0x4E,0x5E]: return "lsr"
        if opcode in [0xEA]: return "nop"
        if opcode in [0x09,0x05,0x15,0x0D,0x1D,0x19,0x01,0x11]: return "ora"
        if opcode in [0xAA]: return "tax"
        if opcode in [0x8A]: return "txa"
        if opcode in [0xCA]: return "dex"
        if opcode in [0xE8]: return "inx"
        if opcode in [0xA8]: return "tay"
        if opcode in [0x98]: return "tya"
        if opcode in [0x88]: return "dey"
        if opcode in [0xC8]: return "iny"
        if opcode in [0x2A,0x26,0x36,0x2E,0x3E]: return "rol"
        if opcode in [0x6A,0x66,0x76,0x6E,0x7E]: return "ror"
        if opcode in [0x40]: return "rti"
        if opcode in [0x60]: return "rts"
        if opcode in [0xE9,0xE5,0xF5,0xED,0xFD,0xF9,0xE1,0xF1]: return "sbc"
        if opcode in [0x85,0x95,0x8D,0x9D,0x99,0x81,0x91]: return "sta"
        if opcode in [0x9A]: return "txs"
        if opcode in [0xBA]: return "tsx"
        if opcode in [0x48]: return "pha"
        if opcode in [0x68]: return "pla"
        if opcode in [0x08]: return "php"
        if opcode in [0x28]: return "plp"
        if opcode in [0x86,0x96,0x8E]: return "stx"
        if opcode in [0x84,0x94,0x8C]: return "sty"
        return "unknown"

