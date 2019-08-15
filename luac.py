import os
import struct
import array

lua_opcode_types = [
    "ABC",  "ABx", "ABC",  "ABC",
    "ABC",  "ABx", "ABC",  "ABx",
    "ABC",  "ABC", "ABC",  "ABC",
    "ABC",  "ABC", "ABC",  "ABC",
    "ABC",  "ABC", "ABC",  "ABC",
    "ABC",  "ABC", "AsBx", "ABC",
    "ABC",  "ABC", "ABC",  "ABC",
    "ABC",  "ABC", "ABC",  "AsBx",
    "AsBx", "ABC", "ABC", "ABC",
    "ABx",  "ABC"
]

lua_opcode_names = [
    "MOVE",     "LOADK",     "LOADBOOL", "LOADNIL",
    "GETUPVAL", "GETGLOBAL", "GETTABLE", "SETGLOBAL",
    "SETUPVAL", "SETTABLE",  "NEWTABLE", "SELF",
    "ADD",      "SUB",       "MUL",      "DIV",
    "MOD",      "POW",       "UNM",      "NOT",
    "LEN",      "CONCAT",    "JMP",      "EQ",
    "LT",       "LE",        "TEST",     "TESTSET",
    "CALL",     "TAILCALL",  "RETURN",   "FORLOOP",
    "FORPREP",  "TFORLOOP",  "SETLIST",  "CLOSE",
    "CLOSURE",  "VARARG"
]

# at [p]osition to k
def get_bits(num, p, k):
    # convert number into binary first 
    binary = bin(num) 

    # remove first two characters 
    binary = binary[2:] 

    # fill in missing bits
    for i in range(32 - len(binary)):
        binary = '0' + binary

    end = len(binary) - p + 1
    start = len(binary) - k + 1

    # extract k  bit sub-string 
    kBitSubStr = binary[start : end] 

    # convert extracted sub-string into decimal again 
    return (int(kBitSubStr,2)) 

class LuaCompiler:
    def __init__(self):
        self.luac = "luac5.1"
        self.o_flag = "-o"
        self.temp_out = "out.luac"
        self.chunks = []
        self.chunk = {}
        self.index = 0

    @staticmethod
    def dis_chunk(chunk):
        print("==== [[" + str(chunk['NAME']) + "]] ====\n")
        for z in chunk['PROTOTYPES']:
            print("** decoding proto\n")
            LuaCompiler.dis_chunk(chunk['PROTOTYPES'][z])
        
        print("\n==== [[" + str(chunk['NAME']) + "'s constants]] ====\n")
        for z in chunk['CONSTANTS']:
            i = chunk['CONSTANTS'][z]
            print(str(z) + ": " + str(i['DATA']))

        print("\n==== [[" + str(chunk['NAME']) + "'s dissassembly]] ====\n")

        for z in chunk['INSTRUCTIONS']:
            i = chunk['INSTRUCTIONS'][z]
            if (i['TYPE'] == "ABC"):
                print(lua_opcode_names[i['OPCODE']], i['A'], i['B'], i['C'])
            elif (i['TYPE'] == "ABx"):
                if (i['OPCODE'] == 1 or i['OPCODE'] == 5):
                    print(lua_opcode_names[i['OPCODE']], i['A'], -i['Bx']-1, chunk['CONSTANTS'][i['Bx']]['DATA'])
                else:
                    print(lua_opcode_names[i['OPCODE']], i['A'], -i['Bx']-1)
            elif (i['TYPE'] == "AsBx"):
                print("AsBx", lua_opcode_names[i['OPCODE']], i['A'], i['sBx'])

    def get_byte(self):
        b = self.bytecode[self.index]
        self.index = self.index + 1
        return b

    def get_int32(self):
        i = 0
        if (self.big_endian):
            i = int.from_bytes(self.bytecode[self.index:self.index+4], byteorder='big', signed=False)
        else:
            i = int.from_bytes(self.bytecode[self.index:self.index+4], byteorder='little', signed=False)
        self.index = self.index + self.int_size
        return i

    def get_int(self):
        i = 0
        if (self.big_endian):
            i = int.from_bytes(self.bytecode[self.index:self.index+self.int_size], byteorder='big', signed=False)
        else:
            i = int.from_bytes(self.bytecode[self.index:self.index+self.int_size], byteorder='little', signed=False)
        self.index = self.index + self.int_size
        return i

    def get_size_t(self):
        s = ''
        if (self.big_endian):
            s = int.from_bytes(self.bytecode[self.index:self.index+self.size_t], byteorder='big', signed=False)
        else:
            s = int.from_bytes(self.bytecode[self.index:self.index+self.size_t], byteorder='little', signed=False)
        self.index = self.index + self.size_t
        return s

    def get_double(self):
        if self.big_endian:
            f = struct.unpack('>d', bytearray(self.bytecode[self.index:self.index+8]))
        else:
            f = struct.unpack('<d', bytearray(self.bytecode[self.index:self.index+8]))
        self.index = self.index + 8
        return f[0]

    def get_string(self, size):
        if (size == None):
            size = self.get_size_t()
            if (size == 0):
                return None
        
        s = "".join(chr(x) for x in self.bytecode[self.index:self.index+size])
        self.index = self.index + size
        return s

    def decode_chunk(self):
        chunk = {
            'INSTRUCTIONS': {},
            'CONSTANTS': {},
            'PROTOTYPES': {}
        }

        chunk['NAME'] = self.get_string(None)
        chunk['FIRST_LINE'] = self.get_int()
        chunk['LAST_LINE'] = self.get_int()

        chunk['UPVALUES'] = self.get_byte()
        chunk['ARGUMENTS'] = self.get_byte()
        chunk['VARG'] = self.get_byte()
        chunk['STACK'] = self.get_byte()

        if (not chunk['NAME'] == None):
            chunk['NAME'] = chunk['NAME'][1:-1]

        # parse instructions
        print("** DECODING INSTRUCTIONS")

        num = self.get_int()
        for i in range(num):
            instruction = {
                # opcode = opcode number;
                # type   = [ABC, ABx, AsBx]
                # A, B, C, Bx, or sBx depending on type
            }

            data   = self.get_int32()
            opcode = get_bits(data, 1, 6)
            tp   = lua_opcode_types[opcode]

            instruction['OPCODE'] = opcode
            instruction['TYPE'] = tp
            instruction['A'] = get_bits(data, 7, 14)

            if instruction['TYPE'] == "ABC":
                instruction['B'] = get_bits(data, 24, 32)
                instruction['C'] = get_bits(data, 15, 23)
            elif instruction['TYPE'] == "ABx":
                instruction['Bx'] = get_bits(data, 15, 32)
            elif instruction['TYPE'] == "AsBx":
                instruction['sBx'] = get_bits(data, 15, 32) - 131071

            chunk['INSTRUCTIONS'][i] = instruction

            print(lua_opcode_names[opcode], instruction)

        # get constants
        print("** DECODING CONSTANTS")

        num = self.get_int()
        for i in range(num):
            constant = {
                # type = constant type;
                # data = constant data;
            }
            constant['TYPE'] = self.get_byte()

            if constant['TYPE'] == 1:
                constant['DATA'] = (self.get_byte() != 0)
            elif constant['TYPE'] == 3:
                constant['DATA'] = self.get_double()
            elif constant['TYPE'] == 4:
                constant['DATA'] = self.get_string(None)[:-1]

            print(constant)
            
            chunk['CONSTANTS'][i] = constant

        # parse protos

        print("** DECODING PROTOS")

        num = self.get_int()
        for i in range(num):
            chunk['PROTOTYPES'][i] = self.decode_chunk()

        # debug stuff
        print("** DECODING DEBUG SYMBOLS")

        # line numbers
        num = self.get_int()
        for i in range(num):
            self.get_int32()

        # locals
        num = self.get_int()
        for i in range(num):
            print(self.get_string(None)[:-1]) # local name
            self.get_int32() # local start PC
            self.get_int32() # local end   PC

        # upvalues
        num = self.get_int()
        for i in range(num):
            self.get_string(None) # upvalue name

        self.chunks.append(chunk)

        return chunk
        
    def decode_rawbytecode(self, rawbytecode):
        # bytecode sanity checks
        if not rawbytecode[0:4] == b'\x1bLua':
            print("Lua Bytecode expected!")
            exit(0)
            
        bytecode   = array.array('b', rawbytecode)
        return self.decode_bytecode(bytecode)

    def decode_bytecode(self, bytecode):
        self.bytecode   = bytecode

        # alligns index lol
        self.index = 4
        
        self.vm_version = self.get_byte()
        self.bytecode_format = self.get_byte()
        self.big_endian = (self.get_byte() == 0)
        self.int_size   = self.get_byte()
        self.size_t     = self.get_byte()
        self.instr_size = self.get_byte() # gets size of instructions
        self.l_number_size = self.get_byte() # size of lua_Number
        self.integral_flag = self.get_byte()
        

        print("Lua VM version: ", hex(self.vm_version))
        print("Big Endian: ", self.big_endian)
        print("int_size: ", self.int_size)
        print("size_t: ", self.size_t)

        #print(self.bytecode)
        self.chunk = self.decode_chunk()
        return self.chunk
        
    def compileC(self, luafile):
        os.system(self.luac + " " + self.o_flag + " " + self.temp_out + " " + luafile)

        with open(self.temp_out, 'rb') as luac_file:
            bytecode = luac_file.read()
            return self.decode_rawbytecode(bytecode)

    def print_dissassembly(self):
        LuaCompiler.dis_chunk(self.chunk)

