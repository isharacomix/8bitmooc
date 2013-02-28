
# My NES assembler. While it's probably a dumb idea to go and roll one of
# my own, I figure it'll be a fun project while I get 8bitmooc off the ground.


# This refers to a $2000-byte Bank of memory. Each bank is physically addressed
# from $0000 to $1FFF, but is logically set to start at a specific starting
# position.
class Bank(object):
    def __init__(self, start):
        self.org = start
        self.start = start
        self.rom = [0]*0x2000


# Here we return two values: (rom, errors)
#   .rom    Which contains the binary
#   .error  Which contains a list of all errors and warnings.
#
# If there was an error, we return a binary of length 0.
def assemble(code):
    elements = parse(code)
    
    # Handle includes.
    # handle incbins (basically add '.bytes' directives in the code)
    
    # First pass: Identify the values of labels by counting the size of the
    # operations based on addressing modes and identifying the .org directives.
    labels = {}
    org = 0
    for label, op, arg, original in elements:
        if label:
            labels[label] = org
        if op:
            if op[0] != '.': org += size(op, arg)
            elif op == ".org": org = num(arg)
            elif op == ".byte": org += 1
            elif op == ".bytes": org += len(arg.split(','))
            elif op == ".ascii": org += len(arg-2)
            elif op == ".define":
                lab, val = arg.split('=')
                labels[lab] = num(val)
    
    # Second pass, iterate over each element and generate the binary.
    # Long and unpythonic. Get over it.
    banks = []
    b = None
    errors, warnings = [],[]
    for label, op, arg, original in elements:            ################### OPS
        if op == '.bank':                                                  #
            index = 0                                                      #
            start = 0                                                      #
            if '=' in arg:                                                 #
                index,start=arg.split('=')                                 #
                index = int(index)                                         #
                start = num(start)                                         #
            else:                                                          #
                index = int(arg)                                           #
                                                                           #
            # Create a new bank if we have to.                             #
            if index == len(banks):                                        #
                banks.append(Bank(start))                                  #
            b = banks[index]                                               #
                                                                           #
        elif op == '.org':                                                 #
            b.org = num(arg)                                               #
        elif op == '.byte':                                                #
            b.rom[b.org-b.start] = num(arg)                                #
            b.org += 1                                                     #
        elif op == '.bytes':                                               #
            for byte in arg.split(','):                                    #
                b.rom[b.org-b.start] = num(byte.strip())                   #
                b.org += 1                                                 #
                
        elif op == 'adc':pass
                                                        ####################
    
    # TODO set the ines header.
    romstring = ""
    for b in banks:
        for c in b.rom: romstring += "%c"%c
    
    # If there are any errors, nothing is assembled.
    if len(errors) > 0: return "", warnings
    else:               return romstring, warnings


# This takes a string of sourcecode (seperated by newlines) and then breaks
# it into four-tuples: label, opcode, arg, original line w/ line number.
def parse( code, source="code" ):
    # Strip the comments and whitespace.
    stripped = [uncomment(l.lower()).strip() for l in code.splitlines()]
    
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
        tokens.append((label,op,data,"("+source+") Line "+str(i)+": "+code[i]))
    return tokens


# This takes a line and gets rid of the comments.
# TODO handle quoted semicolons.
def uncomment(line):
    if ';' not in line: return line
    return line.split(';')[0]


# This returns the addressing mode of the ARG and the number (if present).
# Note that this doesn't actually verify that the number is formatted correctly.
# The num() function takes care of that.
def addrmode(arg):
    if arg == '': return "implied", None
    if arg == 'a': return "register", None
    if arg.startswith("#"): return "immediate", arg[1:]
    if arg.endswith(",y"): return "absolute,y", arg[:-2]
    if arg.startswith('(') and arg.endswith(",x)"): return "indirect,x", arg[1:-3]
    if arg.startswith('(') and arg.endswith("),y"): return "indirect,y", arg[1:-3]
    
    if arg.endswith(",x"):
        arg = arg[:-2]
        if arg.startswith(">") or arg.startswith("<"): return "zero page,x", arg
        if haslabel(arg): return "absolute,x", arg
        x = num(argnum) & 0xff00
        if (x == 0 or x == 0xff00): return "zero page,x", arg
        return "absolute,x", arg
        
    if arg.startswith(">") or arg.startswith("<"): return "zero page", arg
    if haslabel(arg): return "absolute", arg
    x = num(argnum) & 0xff00
    if (x == 0 or x == 0xff00): return "zero page", arg
    return "absolute", arg


# Converts a string to an integer.
# TODO: Support basic arithmetic
def num(s):
    neg = 1
    if s == "0": return 0
    elif s.startswith("0x"): return int(s[2:],16) * neg
    elif s.startswith("$"): return int(s[1:],16) * neg
    elif s.startswith("%"): return int(s[1:],2) * neg
    elif s.startswith("@"): return int(s[1:],8) * neg
    elif s.startswith("0b"): return int(s[2:],2) * neg
    elif s.startswith("0"): return int(s[1:],8) * neg
    elif s.isdigit(): return int(s) * neg
    return None


# Returns true if there's a label in the code.
def haslabel(s):
    if s.startswith("0x"): s = s[2:]
    elif s.startswith("0b"): s = s[2:]
    for c in "abcdefghijklmnopqrstuvwxyz_":
        if c in s: return True
    return False


# Returns the number of bytes (1,2,3) that the line will take up when assembled.
def size(op, arg):
    if op == "nop": return 1
    if op in ["bpl","bmi","bvc","bvs","bcc","bcs","bne","beq"]: return 2
    if op == "brk": return 3
    
    argmode, argnum = addrmode(arg)
    
    # Identify the addressing mode based on the addressing modes and the sizes
    # of the arguments. Here, we assume that all labels are words long, so if
    # we see any labels in the arg, we just say it's a word long.
    if argnum is None: return 1
    if argmode in ["register"]: return 1
    if argmode in ["zero page,x", "zero page"]: return 2
    if argmode in ["indirect,x", "indirect,y", "absolute,y", "immediate"
                   "absolute,x", "absolute"]: return 3

