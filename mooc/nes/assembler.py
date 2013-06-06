# -*- coding: utf-8 -*-

# My NES assembler. While it's probably a dumb idea to go and roll one of
# my own, I figure it'll be a fun project while I get 8bitmooc off the ground.

from django.core import exceptions

from nes.models import Pattern

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
        self.org = 0xC000
        self.start = 0xC000
        self.prg = [0xff]*0x4000
        self.chr = [0xff]*0x2000
        self.labels = {}
        self.errors = []
        self.lastline = ""

    # Here we return two values: (rom, errors)
    #   .rom    Which contains the binary
    #   .error  Which contains a list of all errors and warnings.
    #
    # If there was an error, we return a binary of length 0.
    def assemble(self, code, pattern=None, preamble="", postamble=""):
        pre_elements = []
        post_elements = []
        
        # Try to load the sprite sheet for this code. We expect it to be an
        # actual pattern object.
        if pattern is not None:
            try:
                for i in range(len(pattern.code)/2):
                    self.chr[i] = int(pattern.code[i*2:i*2+2],16)
            except:
                self.err("The pattern %s is corrupt"%pattern)
        
        # Tokenize the code, preamble, and postamble.
        if preamble != "": pre_elements = self.parse(preamble, "preamble")
        if postamble != "": post_elements = self.parse(postamble, "postamble")
        elements = self.parse(code)
        
        # Pass zero: handle .includes, which connect to the
        # Assembler model. The database stores the includes as
        # textfiles to be imported
        new_elements = []
        for label, op, arg, original in pre_elements+elements+post_elements:
            if op in [".include", ".ascii"] and (arg is None or
                            not (arg.startswith('"') and arg.endswith('"'))):
                self.err("Incorrectly formatted quoted string")
            elif op == ".include":
                arg = arg[1:-1]
                try: kern = Kernal.objects.get(name=arg)
                except exceptions.ObjectDoesNotExist:
                    self.err("No such kernal "+arg)
                inc_elements = self.parse(kern.code, arg)
                new_elements += inc_elements
            elif op == ".ascii":
                arg = arg[1:-1]
                new_arg = ""
                skip = False
                for c in arg:
                    try: x = ord(c)
                    except: x = 0
                    if skip:
                        skip = False
                        new_arg += "$%x,"%x
                    elif c == '\\': skip = True
                    else: new_arg += "$%x,"%x
                new_elements.append((label, ".db", new_arg.strip(','), original))
            else:
                new_elements.append((label, op, arg, original))
        elements = new_elements
        
        # If we came across any errors in pass zero, don't proceed to pass one.
        if len(self.errors) > 0: return "", self.errors
        
        # First pass: Identify the values of labels by counting the size of the
        # operations based on addressing modes and identifying the .org directives.
        for label, op, arg, original in elements:
            self.lastline = original
            if label:
                self.labels[label] = self.org
                if len(label) == 0 or label[0] not in "abcdefghijklmnopqrstuvwxyz_":
                    self.err("Labels may only start with letters or underscore")
                for c in label:
                    if c not in "abcdefghijklmnopqrstuvwxyz0123456789_":
                        self.err("Illegal character in label name")
            if op:
                if   op[0] != '.': self.org += self.size(op, arg)
                elif op == ".org": self.org = self.num(arg)
                elif op == ".byte": self.org += 1
                elif op == ".word" or op == ".dw": self.org += 2
                elif op == ".bytes" or op == ".db": self.org += len(arg.split(','))
                elif op == ".define":
                    lab, val = arg.split('=')
                    self.labels[lab] = self.num(val)
                    if len(lab) == 0 or lab[0] not in "abcdefghijklmnopqrstuvwxyz_":
                        self.err("Labels may only start with letters or underscore")
                    for c in lab:
                        if c not in "abcdefghijklmnopqrstuvwxyz0123456789_":
                            self.err("Illegal character in label name")
        
        # If we came across any errors in pass one, don't proceed to pass two.
        if len(self.errors) > 0: return "", self.errors
        
        # Second pass, iterate over each element and generate the binary.
        # Uses the symbol table to match opcodes with addressing modes.
        self.org = 0xC000
        for label, op, arg, original in elements:
            self.lastline = original
            if   op == '.define': pass
            elif op == '.org':
                self.org = self.num(arg)
            elif op == '.byte':
                self.labels["*"] = self.org+1
                self.write_prg( self.num(arg), self.org )
                self.org += 1
            elif op == '.word' or op == '.dw':
                self.labels["*"] = self.org+2
                val = self.num(arg)
                self.write_prg( val, self.org )
                self.write_prg( val>>8, self.org+1 )
                self.org += 2
            elif op == '.bytes' or op == '.db':
                for byte in arg.split(','):
                    self.labels["*"] = self.org+1
                    self.write_prg( self.num(byte.strip()), self.org )
                    self.org += 1
            elif op in ["stx","ldx"]:
                arg = arg.replace(",y",",x")
                mode, argnum = self.addrmode(arg)
                self.labels["*"] = self.org+2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X]:
                    self.labels["*"] = self.org+3
                symbol = SYMBOL_TABLE[op][mode]
                val = self.num(argnum)
                if not symbol:
                    self.err("Incorrect addressing mode for %s"%op)
                self.write_prg( symbol, self.org )
                self.write_prg( val, self.org+1 )
                self.org += 2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X]:
                    self.write_prg( val>>8, self.org )
                    self.org += 1
            elif op in ["bpl","bmi","bvc","bvs","bcc","bcs","bne","beq"]:
                self.labels["*"] = self.org+2
                self.write_prg( SYMBOL_TABLE[op], self.org )
                self.write_prg( self.num(arg)-self.org-2, self.org+1 )
                self.org += 2
            elif op == 'jsr':
                self.labels["*"] = self.org+3
                self.write_prg( SYMBOL_TABLE[op], self.org )
                val = self.num(arg)
                self.write_prg( val, self.org+1 )
                self.write_prg( val>>8, self.org+2 )
                self.org += 3
            elif op == 'jmp':
                self.labels["*"] = self.org+3
                if arg.startswith('(') and arg.endswith(')'):
                    self.write_prg( SYMBOL_TABLE[op][1], self.org )
                    arg = arg[1:-1]
                else:
                    self.write_prg( SYMBOL_TABLE[op][0], self.org )
                mode, argnum = self.addrmode(arg)
                if mode not in [M_ZEROPAGE, M_ABSOLUTE]:
                    self.err("Incorrect addressing mode for %s"%op)
                val = self.num(argnum)
                self.write_prg( val, self.org+1 )
                self.write_prg( val>>8, self.org+2 )
                self.org += 3
            elif op == 'brk':
                self.labels["*"] = self.org+2
                self.write_prg( SYMBOL_TABLE[op], self.org )
                val = self.num(arg)
                mode, argnum = self.addrmode(arg)
                if mode not in [M_IMMEDIATE]:
                    self.err("Incorrect addressing mode for %s"%op)
                self.write_prg( val, self.org+1 )
                self.org += 2
            elif op in SYMBOL_TABLE:
                mode, argnum = self.addrmode(arg)
                symbol = SYMBOL_TABLE[op][mode]
                if not symbol:
                    self.err("Incorrect addressing mode for %s"%op)
                    symbol = 0xFF
                self.labels["*"] = self.org+2
                if mode in [M_ABSOLUTE,M_ABSOLUTE_X,M_ABSOLUTE_Y]:
                    self.labels["*"] = self.org+3
                if mode in [M_IMPLIED,M_REGISTER]:
                    self.labels["*"] = self.org+1
                    self.write_prg( symbol, self.org )
                    self.org += 1
                else:
                    val = self.num(argnum)
                    self.write_prg( symbol, self.org )
                    self.write_prg( val, self.org+1 )
                    self.org += 2
                    if mode in [M_ABSOLUTE,M_ABSOLUTE_X,M_ABSOLUTE_Y]:
                        self.write_prg( val>>8, self.org )
                        self.org += 1
            elif op is None or op == "": pass
            else: self.err("Illegal opcode/directive %s"%op)
        
        # Set the ines header. We don't honor different mapper bits.
        header = [ 0x4E, 0x45, 0x53, 0x1A, 1, 1, 1, 0,
                   0, 0, 0 , 0, 0, 0, 0 , 0]
        
        # If there are any errors, nothing is assembled.
        if len(self.errors) > 0: return "", self.errors
        
        # Otherwise, put it all together and see what we get!
        romstring = ""
        for c in header + self.prg + self.chr:
            romstring += "%c"%(c&0xff)
        return romstring, self.errors

    
    # This writes to the code, getting rid of out-of-bounds exceptions.
    def write_prg(self, byte, i):
        i = i-self.start
        if i >= 0 and i < 0x4000:
            self.prg[i] = byte & 0xff
        else:
            self.err("Wrote outside of valid ROM")
        

    # This takes a string of sourcecode (seperated by newlines) and then breaks
    # it into four-tuples: label, opcode, arg, original line w/ line number.
    # Should return no errors.
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
            arg = None
            if ":" in line:
                label, line = line.split(':',1)
                label = label.strip()
                line = line.strip()
            if line:
                items = line.split(None,1)
                op = items[0]
                if len(items) == 2: arg = items[1].replace(' ','')
            tokens.append((label,op,arg,"("+source+") Line "+str(i+1)+": "+codelines[i]))
        return tokens


    # This returns the addressing mode of the ARG and the number (if present).
    # Note that this doesn't actually verify that the number is formatted correctly.
    # The num() function takes care of that. Should return no errors.
    # There should be no whitespace in the args - the parser ensures that.
    def addrmode(self, arg):
        if arg == '' or arg is None: return M_IMPLIED, None
        if arg == 'a': return M_REGISTER, None
        if arg.startswith('(') and arg.endswith('),y'): return M_INDIRECT_Y, arg[1:-3]
        if arg.startswith('(') and arg.endswith(',x)'): return M_INDIRECT_X, arg[1:-3]
        if arg.startswith("#"): return M_IMMEDIATE, arg[1:]
        if arg.endswith(",y"): return M_ABSOLUTE_Y, arg[:-2]
        
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


    # A legal number is a set of alphanumeric strings seperated by + and -.
    # If the number is bad, the error bubbles up from 'getnum', but we catch
    # illegal characters in numbers here.
    def num(self, s):
        report = 0
        mask = 0xffff
        if s.startswith('>'): mask, s = 0xff, s[1:]
        if s.startswith('<'): mask, s = 0xff00, s[1:]
        
        for c in s:
            if c not in "abcdefghijklmnopqrstuvwxyz0123456789_*-+%$@":
                self.err("Only addition and subtraction are allowed for numbers.")
                return 0
        
        # We first split by the + signs, and then we split on the '-' signs.
        nums = s.split('+')
        for n in nums:
            if '-' in n:
                negnums = n.split('-')
                if n.startswith('-'):
                    report -= self.parsenum(negnums[1])
                    for neg in negnums[2:]: report -= self.parsenum(neg)
                else:
                    report += self.parsenum(negnums[0])
                    for neg in negnums[1:]: report -= self.parsenum(neg)
            else: report += self.parsenum(n)
        
        # Mask the result and return it. We simply wrap overflow around.
        report = report & mask
        if mask == 0xff00: report = (report >> 8)&0xff
        return report
    
    
    # Converts a string to an integer. Returns an error if the string is
    # improperly formatted or if there is no such label with the given name.
    def parsenum(self, s):
        try:
            if s == "0": return 0
            elif s.startswith("0x"): return int(s[2:],16)
            elif s.startswith("$"): return int(s[1:],16)
            elif s.startswith("%"): return int(s[1:],2)
            elif s.startswith("@"): return int(s[1:],8)
            elif s.startswith("0b"): return int(s[2:],2)
            elif s.startswith("0"): return int(s[1:],8)
            elif s.isdigit(): return int(s)
        except ValueError:
            self.err("Improperly formatted number")
            return 0
            
        if s in self.labels: return self.labels[s]
        else:
            self.err("Unknown label: '%s'"%s)
            return 0


    # Returns true if there's a label in the code.
    # Should not return any errors.
    def haslabel(self, s):
        if s.startswith("0x"): s = s[2:]
        elif s.startswith("0b"): s = s[2:]
        for c in "abcdefghijklmnopqrstuvwxyz_*":
            if c in s: return True
        return False


    # Returns the number of bytes (1,2,3) that the line will take up when assembled.
    # Should not return any errors.
    def size(self, op, arg):
        if op in ["brk","bpl","bmi","bvc","bvs","bcc","bcs","bne","beq"]: return 2
        if op in ['jmp','jsr']: return 3
        
        argmode, argnum = self.addrmode(arg)
        
        # Identify the addressing mode based on the addressing modes and the sizes
        # of the arguments. Here, we assume that all labels are words long, so if
        # we see any labels in the arg, we just say it's a word long.
        if argnum is None: return 1
        if argmode in [M_REGISTER, M_IMPLIED]: return 1
        if argmode in [M_ZEROPAGE, M_ZEROPAGE_X, M_INDIRECT_X,
                       M_INDIRECT_Y, M_IMMEDIATE]: return 2
        if argmode in [M_ABSOLUTE_Y, M_ABSOLUTE_X, M_ABSOLUTE]: return 3
        self.err("IMPOSSIBLE! addrmode returned a nonexistant addressing type")


    # This takes a line and gets rid of the comments.
    # Should not return any errors.
    def uncomment(self,line):
        if ';' not in line: return line
        if not line.startswith('.ascii'): return line.split(';')[0]
        killpoint = None
        safe = True
        i = line.index('"')
        while not killpoint and i < len(line):
            if line[i] == ';' and not safe: killpoint = i
            if line[i] == '"' and line[i-1] != "\\": safe = False
        return line[:killpoint]
    
    
    # Add an error string to the list of errors.
    def err(self,s):
        if len(self.errors) < 100:
            e = "["+s+"] "+self.lastline
            if e not in self.errors:
                self.errors.append(e)


# This function assembles a ROM and stores it in the session parameter. Returns
# True if successful and false if there are compilation errors. This function
# will also take assembly constraints (based on user level, etc) into account.
def assemble_and_store(request, name, code, pattern=None, preamble="", postamble=""):
    A = Assembler()
    
    # Try to get the pattern by the name specifed.
    if pattern not in Pattern.objects.all(): pattern = None
    
    # Compile the ROM and store it as a session variable. If it fails, then
    # a None will be stored in its place (successfully resulting in a 404).
    rom, errors = A.assemble( code, pattern, preamble, postamble )
    request.session["rom"] = rom
    request.session["rom_name"] = name
    
    # Collect the alerts and store them in the 
    if "alerts" not in request.session: request.session["alerts"] = []
    for e in errors: request.session["alerts"].append( ("alert-error", e) )
    
    # Return True or False based on success or failure.
    return True if rom else False

