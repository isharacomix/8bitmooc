# -*- coding: utf-8 -*-

# My NES assembler. While it's probably a dumb idea to go and roll one of
# my own, I figure it'll be a fun project while I get 8bitmooc off the ground.


# This refers to a $2000-byte Bank of memory. Each bank is physically addressed
# from $0000 to $1FFF, but is logically set to start at a specific starting
# position.
class Bank(object):
    def __init__(self, start, size=0x2000):
        self.org = start
        self.start = start
        self.size = size
        self.rom = [0xff]*self.size
        self.inesprg = 0
        self.ineschr = 0
        self.inesmap = 0
        self.inesmir = 0


# Addressing modes.
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

# Opcode Table
SYMBOL_TABLE = {   #IMP, REG, IMM, ZPG, ZPX, ABS, ABX, ABY, INX, INY,
          "adc": [ None,None,0x69,0x65,0x75,0x6D,0x7D,0x79,0x61,0x71 ],
          "and": [ None,None,0x29,0x25,0x35,0x2D,0x3D,0x39,0x21,0x31 ],
          "asl": [ None,0x0A,None,0x06,0x16,0x0E,0x1E,None,None,None ],
          "bit": [ None,None,None,0x24,None,0x2C,None,None,None,None ],
          "bpl": 0x10,                                                  #sp case
          "bmi": 0x30,                                                  #sp case
          "bvc": 0x50,                                                  #sp case
          "bvs": 0x70,                                                  #sp case
          "bcc": 0x90,                                                  #sp case
          "bcs": 0xB0,                                                  #sp case
          "bne": 0xD0,                                                  #sp case
          "beq": 0xF0,                                                  #sp case
          "brk": 0x00,                                                  #sp case
          "cmp": [ None,None,0xC9,0xC5,0xD5,0xCD,0xDD,0xD9,0xC1,0xD1 ],
          "cpx": [ None,None,0xE0,0xE4,None,0xEC,None,None,None,None ],
          "cpy": [ None,None,0xC0,0xC4,None,0xCC,None,None,None,None ],
          "dec": [ None,None,None,0xC6,0xD6,0xCE,0xDE,None,None,None ],
          "eor": [ None,None,0x49,0x45,0x55,0x4D,0x5D,0x59,0x41,0x51 ],
          "clc": [ 0x18,None,None,None,None,None,None,None,None,None ],
          "sec": [ 0x38,None,None,None,None,None,None,None,None,None ],
          "cli": [ 0x58,None,None,None,None,None,None,None,None,None ],
          "sei": [ 0x78,None,None,None,None,None,None,None,None,None ],
          "clv": [ 0xB8,None,None,None,None,None,None,None,None,None ],
          "cld": [ 0xD8,None,None,None,None,None,None,None,None,None ],
          "sed": [ 0xF8,None,None,None,None,None,None,None,None,None ],
          "inc": [ None,None,None,0xE6,0xF6,0xEE,0xFE,None,None,None ],
          "jmp": (0x4C,0x6C),                                           #sp case
          "jsr": 0x20,                                                  #sp case
          "lda": [ None,None,0xA9,0xA5,0xB5,0xAD,0xBD,0xB9,0xA1,0xB1 ],
          "ldx": [ None,None,0xA2,0xA6,0xB6,0xAE,0xBE,None,None,None ], #sp case
          "ldy": [ None,None,0xA0,0xA4,0xB4,0xAC,0xBC,None,None,None ],
          "lsr": [ None,0x4A,None,0x46,0x56,0x4E,0x5E,None,None,None ],
          "nop": [ 0xEA,None,None,None,None,None,None,None,None,None ],
          "ora": [ None,None,0x09,0x05,0x15,0x0D,0x1D,0x19,0x01,0x11 ],
          "tax": [ 0xAA,None,None,None,None,None,None,None,None,None ],
          "txa": [ 0x8A,None,None,None,None,None,None,None,None,None ],
          "dex": [ 0xCA,None,None,None,None,None,None,None,None,None ],
          "inx": [ 0xE8,None,None,None,None,None,None,None,None,None ],
          "tay": [ 0xA8,None,None,None,None,None,None,None,None,None ],
          "tya": [ 0x98,None,None,None,None,None,None,None,None,None ],
          "dey": [ 0x88,None,None,None,None,None,None,None,None,None ],
          "iny": [ 0xC8,None,None,None,None,None,None,None,None,None ],
          "rol": [ None,0x2A,None,0x26,0x36,0x2E,0x3E,None,None,None ],
          "ror": [ None,0x6A,None,0x66,0x76,0x6E,0x7E,None,None,None ],
          "rti": [ 0x40,None,None,None,None,None,None,None,None,None ],
          "rts": [ 0x60,None,None,None,None,None,None,None,None,None ],
          "sbc": [ None,None,0xE9,0xE5,0xF5,0xED,0xFD,0xF9,0xE1,0xF1 ],
          "sta": [ None,None,None,0x85,0x95,0x8D,0x9D,0x99,0x81,0x91 ],
          "txs": [ 0x9A,None,None,None,None,None,None,None,None,None ],
          "tsx": [ 0xBA,None,None,None,None,None,None,None,None,None ],
          "pha": [ 0x48,None,None,None,None,None,None,None,None,None ],
          "pla": [ 0x68,None,None,None,None,None,None,None,None,None ],
          "php": [ 0x08,None,None,None,None,None,None,None,None,None ],
          "plp": [ 0x28,None,None,None,None,None,None,None,None,None ],
          "stx": [ None,None,None,0x86,0x96,0x8E,None,None,None,None ], #sp case
          "sty": [ None,None,None,0x84,0x94,0x8C,None,None,None,None ],
                   #IMP, REG, IMM, ZPG, ZPX, ABS, ABX, ABY, INX, INY
               }



#
class Assembler(object):
    def __init__(self):
        self.labels = {}
        self.warnings = []
        self.errors = []

    # Here we return two values: (rom, errors)
    #   .rom    Which contains the binary
    #   .error  Which contains a list of all errors and warnings.
    #
    # If there was an error, we return a binary of length 0.
    def assemble(self, code):
        elements = self.parse(code)
        
        # Handle includes.
        # handle incbins (basically add '.bytes' directives in the code)
        
        # First pass: Identify the values of labels by counting the size of the
        # operations based on addressing modes and identifying the .org directives.
        banks = []
        b = None
        for label, op, arg, original in elements:
            if label:
                self.labels[label] = b.org
            if op:
                if op == '.bank': 
                    index = 0
                    start = 0
                    if '=' in arg: 
                        index,start=arg.split('=') 
                        index = int(index)
                        start = self.num(start)
                    else: index = int(arg)
                    if index == len(banks):
                        banks.append(Bank(start))
                    b = banks[index]
                elif op[0] != '.': b.org += self.size(op, arg)
                elif op == ".org": b.org = self.num(arg)
                elif op == ".byte": b.org += 1
                elif op == ".word" or op == ".dw": b.org += 2
                elif op == ".bytes" or op == ".db": b.org += len(arg.split(','))
                elif op == ".ascii": b.org += len(arg-2)
                elif op == ".define":
                    lab, val = arg.split('=')
                    self.labels[lab] = self.num(val)
        
        # Second pass, iterate over each element and generate the binary.
        # Uses the symbol table to match opcodes with addressing modes.
        banks = []
        b = None
        for label, op, arg, original in elements:
            print ">>>"+original
            if op == '.bank':
                index = 0
                start = 0
                if '=' in arg:
                    index,start=arg.split('=')
                    index = int(index)
                    start = self.num(start)
                else: index = int(arg)
                if index == len(banks):
                    banks.append(Bank(start))
                b = banks[index]
            elif op == '.inesprg':
                self.inesprg = int(arg)
            elif op == '.ineschr':
                self.ineschr = int(arg)
            elif op == '.inesmap':
                self.inesmap = int(arg)
            elif op == '.inesmir':
                self.inesmir = int(arg)
            elif op == '.org':
                b.org = self.num(arg)
            elif op == '.byte':
                self.labels["*"] = b.org+1
                b.rom[b.org-b.start] = self.num(arg)&0xff
                b.org += 1
            elif op == '.word' or op == '.dw':
                self.labels["*"] = b.org+2
                val = self.num(arg)
                b.rom[b.org-b.start] = val&0xff
                b.rom[b.org-b.start+1] = (val>>8)&0xff
                b.org += 2
            elif op == '.bytes' or op == '.db':
                for byte in arg.split(','):
                    self.labels["*"] = b.org+1
                    b.rom[b.org-b.start] = self.num(byte.strip())&0xff
                    b.org += 1
            elif op in ["stx","ldx"]:
                arg = arg.replace(",y",",x")
                mode, argnum = self.addrmode(arg)
                self.labels["*"] = b.org+2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X]:
                    self.labels["*"] = b.org+3
                symbol = SYMBOL_TABLE[op][mode]
                val = self.num(argnum)
                if not symbol: pass #raise error                        
                b.rom[b.org-b.start] = symbol
                b.rom[b.org-b.start+1] = val&0xff
                b.org += 2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X]:
                    b.rom[b.org-b.start] = (val>>8)&0xff
                    b.org += 1
            elif op in ["bpl","bmi","bvc","bvs","bcc","bcs","bne","beq","brk"]:
                self.labels["*"] = b.org+2
                b.rom[b.org-b.start] = SYMBOL_TABLE[op]
                b.rom[b.org-b.start+1] = self.num(arg)&0xff
                b.org += 2
            elif op == 'jsr':
                self.labels["*"] = b.org+3
                b.rom[b.org-b.start] = SYMBOL_TABLE[op]
                val = self.num(arg)
                b.rom[b.org-b.start+1] = val&0xff
                b.rom[b.org-b.start+2] = (val>>8)&0xff
                b.org += 3
            elif op == 'jmp':
                self.labels["*"] = b.org+3
                if arg.startswith('(') and arg.endswith(')'):
                    b.rom[b.org-b.start] = SYMBOL_TABLE[op][1]
                    arg = arg[1:-1]
                else:
                    b.rom[b.org-b.start] = SYMBOL_TABLE[op][0]
                mode, argnum = self.addrmode(arg)
                if mode not in [M_ZEROPAGE, M_ABSOLUTE]: pass #error!
                val = self.num(argnum)
                b.rom[b.org-b.start+1] = val&0xff
                b.rom[b.org-b.start+2] = (val>>8)&0xff
                b.org += 3
            elif op == 'brk':
                self.labels["*"] = b.org+3
                b.rom[b.org-b.start] = SYMBOL_TABLE[op]
                val = self.num(arg)
                mode, argnum = self.addrmode(arg)
                if mode not in [M_IMMEDIATE]: pass #error!
                b.rom[b.org-b.start+1] = val&0xff
                b.org += 3
            elif op in SYMBOL_TABLE:
                mode, argnum = self.addrmode(arg)
                symbol = SYMBOL_TABLE[op][mode]
                if not symbol: pass #raise error                        
                self.labels["*"] = b.org+2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X,M_ABSOLUTE_Y]:
                    self.labels["*"] = b.org+3
                if mode in [M_IMPLIED,M_REGISTER]:
                    self.labels["*"] = b.org+1
                    b.rom[b.org-b.start] = symbol
                    b.org += 1
                else:
                    val = self.num(argnum)
                    b.rom[b.org-b.start] = symbol
                    b.rom[b.org-b.start+1] = val&0xff
                    b.org += 2
                    if mode in [M_ABSOLUTE,M_ABSOLUTE_X,M_ABSOLUTE_Y]:
                        b.rom[b.org-b.start] = (val>>8)&0xff
                        b.org += 1
        
        # Set the ines header. We don't honor different mapper bits.
        header = [ 0x4E, 0x45, 0x53, 0x1A, self.inesprg, self.ineschr,
                   self.inesmir, 0, 0, 0, 0 , 0, 0, 0, 0 , 0]
        
        # If there are any errors, nothing is assembled.
        if len(self.errors) > 0: return "", self.warnings

        # Otherwise, put it all together and see what we get!
        romstring = ""
        for c in header:
            romstring += "%c"%(c&0xff)
        for b in banks:
            for c in b.rom: romstring += "%c"%(c&0xff)
        return romstring, self.warnings


    # This takes a string of sourcecode (seperated by newlines) and then breaks
    # it into four-tuples: label, opcode, arg, original line w/ line number.
    def parse(self, code, source="code"):
        # Strip the comments and whitespace.
        codelines = code.splitlines()
        stripped = [self.uncomment(l.lower()).strip() for l in codelines]
        
        # Break the code into four-tuples: label, opcode, arg, and original string.
        tokens = []
        for i in range(len(stripped)):
            line = stripped[i]
            label = None
            op = None
            data = None
            if ":" in line:
                label, line = line.split(':',1)
                label = label.strip()
                line = line.strip()
            if line:
                items = line.split(None,1)
                op = items[0]
                if len(items) == 2: data = items[1].replace(' ','')
            tokens.append((label,op,data,"("+source+") Line "+str(i+1)+": "+codelines[i]))
        return tokens


    # This returns the addressing mode of the ARG and the number (if present).
    # Note that this doesn't actually verify that the number is formatted correctly.
    # The num() function takes care of that.
    def addrmode(self, arg):
        if arg == '' or arg is None: return M_IMPLIED, None
        if arg == 'a': return M_REGISTER, None
        if arg.startswith("#"): return M_IMMEDIATE, arg[1:]
        if arg.endswith(",y"): return M_ABSOLUTE_Y, arg[:-2]
        if arg.startswith('(') and arg.endswith(',x)'): return M_INDIRECT_X, arg[1:-3]
        if arg.startswith('(') and arg.endswith('),y'): return M_INDIRECT_Y, arg[1:-3]
        
        if arg.endswith(",x"):
            arg = arg[:-2]
            if arg.startswith(">") or arg.startswith("<"): return M_ZEROPAGE_X, arg
            if self.haslabel(arg): return M_ABSOLUTE_X, arg
            x = self.num(arg) & 0xff00
            if (x == 0 or x == 0xff00): return M_ZEROPAGE_X, arg
            return M_ABSOLUTE_X, arg
            
        if arg.startswith(">") or arg.startswith("<"): return M_ZEROPAGE, arg
        if self.haslabel(arg): return M_ABSOLUTE, arg
        x = self.num(arg) & 0xff00
        if (x == 0 or x == 0xff00): return M_ZEROPAGE, arg
        return M_ABSOLUTE, arg


    # A legal number is a set of alphanumeric strings seperated by + and -
    def num(self, s):
        report = 0
        mask = 0xffff
        if s.startswith('>'): mask, s = 0xff, s[1:]
        if s.startswith('<'): mask, s = 0xff00, s[1:]
        
        for c in s:
            if c not in "abcdefghijklmnopqrstuvwxyz_*-+%$@": pass #raise illegal
        
        # We first split by the + signs, and then we split on the '-' signs.
        nums = s.split('+')
        for n in nums:
            if '-' in n:
                negnums = n.split('-')
                if n.startswith('-'):
                    report -= self.getnum(negnums[1])
                    for neg in negnums[2:]: report -= self.getnum(neg)
                else:
                    report += self.getnum(negnums[0])
                    for neg in negnums[1:]: report -= self.getnum(neg)
            else: report += self.getnum(n)
        
        # Mask the result and return it. We simply wrap overflow around.
        report = report & mask
        if mask == 0xff00: report = (report >> 8)&0xff
        return report
    
    # Converts a string to an integer.
    def getnum(self, s):
        if s == "0": return 0
        elif s.startswith("0x"): return int(s[2:],16)
        elif s.startswith("$"): return int(s[1:],16)
        elif s.startswith("%"): return int(s[1:],2)
        elif s.startswith("@"): return int(s[1:],8)
        elif s.startswith("0b"): return int(s[2:],2)
        elif s.startswith("0"): return int(s[1:],8)
        elif s.isdigit(): return int(s)
        elif s in self.labels: return self.labels[s]
        else: pass #illegal


    # Returns true if there's a label in the code. Returns no errors.
    def haslabel(self, s):
        if s.startswith("0x"): s = s[2:]
        elif s.startswith("0b"): s = s[2:]
        for c in "abcdefghijklmnopqrstuvwxyz_*":
            if c in s: return True
        return False


    # Returns the number of bytes (1,2,3) that the line will take up when assembled.
    # Returns an error if something weird happens.
    def size(self, op, arg):
        if op in ["bpl","bmi","bvc","bvs","bcc","bcs","bne","beq"]: return 2
        if op in ["brk",'jmp','jsr']: return 3
        
        argmode, argnum = self.addrmode(arg)
        
        # Identify the addressing mode based on the addressing modes and the sizes
        # of the arguments. Here, we assume that all labels are words long, so if
        # we see any labels in the arg, we just say it's a word long.
        if argnum is None: return 1
        if argmode in [M_REGISTER, M_IMPLIED]: return 1
        if argmode in [M_ZEROPAGE, M_ZEROPAGE_X, M_INDIRECT_X,
                       M_INDIRECT_Y, M_IMMEDIATE]: return 2
        if argmode in [M_ABSOLUTE_Y, M_ABSOLUTE_X, M_ABSOLUTE]: return 3
        # error here


    # This takes a line and gets rid of the comments.
    def uncomment(self,line):
        if ';' not in line: return line
        if '.ascii' not in line: return line.split(';')[0]
        killpoint = None
        safe = True
        i = line.index('"')
        while not killpoint and i < len(line):
            if line[i] == ';' and not safe: killpoint = i
            if line[i] == '"': safe = False
        return line[:killpoint]


def test(s):
    code = open(s).read()
    a = Assembler()
    x,w = a.assemble(code)
    out = open("test.nes","wb")
    out.write(x)
    out.close()

