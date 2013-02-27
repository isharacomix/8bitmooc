
# My NES assembler. While it's probably a dumb idea to go and roll one of
# my own, I figure it'll be a fun project while I get 8bitmooc off the ground.

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
            elif op == ".bytes": org += 5
            elif op == ".ascii": org += 5
            elif op == ".ascii": org += 5
    
    # Second pass, iterate over each element and generate the binary.
    rom = ""
    errors = []
    warnings = []
    for label, op, arg, original in elements:
        pass
    
    # If there are any errors, nothing is assembled.
    if len(errors) > 0:
        return "", warnings
    else:
        return rom, warnings


# This takes a string of sourcecode (seperated by newlines) and then breaks
# it into four-tuples: label, opcode, arg, original line w/ line number.
def parse( code, source="code" ):
    # Strip the comments and whitespace.
    code = [uncomment(l.lower()).strip() for l in code.splitlines()]
    
    # Break the code into four-tuples: label, opcode, arg, and original string.
    elements = []
    for i in range(len(source)):
        line = code[i]
        label = None
        op = None
        data = None
        if ":" in line:
            label, line = line.split(':',1)
            label = label.strip()
            line = line.strip()
        items = line.split(None,1)
        op = items[0]
        if len(items) == 2: data = items[1]
        elements.append(label,op,data,"("+source+") Line "+str(i)+": "+code[i])
    return elements


# This takes a line and gets rid of the comments.
# TODO handle quoted semicolons.
def uncomment(line):
    if ';' not in line: return line
    return line.split(';')[0]


# Converts a string to an integer.
# TODO: Support basic arithmetic
def num(s):
    neg = 1
    for c in "()#,xya":
        s = s.replace(c,'')
    s = s.split(',')[0]
    if s.startswith("-"):
        neg = -1
        s = s[1:]
    
    if s.startswith("0x"): return int(s[2:],16) * neg
    elif s.startswith("$"): return int(s[1:],16) * neg
    elif s.startswith("%"): return int(s[1:],2) * neg
    elif s.startswith("#"): return int(s[1:],8) * neg
    elif s.startswith("0b"): return int(s[2:],2) * neg
    elif s.startswith("0"): return int(s[1:],8) * neg
    elif s.isdigit(): return int(s) * neg
    return None


# Returns the number of bytes (1,2,3) that the line will take up when assembled.
# This does not require us to see the opcode - only the addressing mode.
def size(line):
    op = line.split(None,1)
    
    if op[0] == "nop": return 1
    elif op[0] in ["bpl","bmi","bvc","bvs","bcc","bcs","bne","beq"]: return 2
    elif len(op) == 1: return 1
    elif ',' in op[1]: return 2
    elif op[1] == "a": return 1
    else:
        n = num(op[1])
        if n is None: return 3
        n &= 0xffff
        if n & 0xff == 0xff or n & 0xff == 0x00: return 2
        else: return 3

