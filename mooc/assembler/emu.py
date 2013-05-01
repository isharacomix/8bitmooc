# -*- coding: utf-8 -*-

# My NES Emulator. It's not perfect, and doesn't really utilize any sort of
# audio/visual elements, but focuses on the register values of the hardware.

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
        self.vram_mirror = 1        # 0 all mirror, 1 vert, 2 horiz, 3 unique
        
        # CPU Registers
        self.A = 0x00               # Accumulator
        self.X = 0x00               # X Index
        self.Y = 0x00               # Y Index
        self.SP = 0x00              # Stack pointer
        self.PC = 0x00              # Program counter
        self.status = 0x00          # Status register
        
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
            for i in in range(0,len(prgrom)):
                self.rom[-1-i] = prgrom[-1-i]
        if chrrom and len(chrrom)==0x2000:
            for i in range(0,0x2000):
                self.vram[i] = chrrom[i]&0xff
    
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

    # These allow you to push buttons on a controller. When the controller is
    # strobed, the buttons will be released automatically.
    # A, B, Select, Start, Up, Down, Left, Right, All
    # 0, 1, 2,      3,     4,  5,    6,    7,     8
    # If 'press' is false, then it is released, not pressed.
    def controller(self, player, button, press=True)
        if press:
            k = (1 << button) if button != 8 else 0xff
            if player == 1: self.p1 |= k
            if player == 2: self.p2 |= k
        else:
            k = (0xff ^ (1 << button)) if button != 8 else 0x00
            if player == 1: self.p1 &= k
            if player == 2: self.p2 &= k

    # This steps through one instruction. It returns something TODO
    def step(self):
        if False: #vblank
            self.vblank = True
            if self.vblank_nmi:
                pass #fire an NMI
            
        pass

