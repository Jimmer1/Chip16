import chip64_util as c16u
import numpy as np
import sys

register_mnemonics = ["r" + hex(i)[2:].upper() for i in range(16)]
device_mnemonics = ["dev" + hex(i)[2:].upper() for i in range(16)]

def tokenise(source_code : str) -> list:
    tokens = []
    str_buffer = []
    comment_flag = False
    for char in source_code:

        if char == '#':
            comment_flag = True
        elif comment_flag and char != '\n':
            continue
        elif comment_flag and char == '\n':
            comment_flag = False
            continue
        
        # if char == "\n":
        #     continue

        if char.isalnum() or char == "_":
            str_buffer.append(char)
        elif char.isspace() or char in ",:":
            if str_buffer != []:
                tokens.append("".join(str_buffer))
            str_buffer = []
            if char in ",:":
                tokens.append(char)

    if str_buffer != []:
        tokens.append("".join(str_buffer))
    return tokens

def build_opcode(ops):
    if len(ops) == 4:
        assert ops[0] < 0x10 and ops[1] < 0x10 and ops[2] < 0x10 and ops[3] < 0x10

        return np.uint16(
            (ops[0] << 12) | (ops[1] << 8) | (ops[2] << 4) | ops[3]
        )
    elif len(ops) == 3:
        assert 0 <= ops[0] < 0x10 and 0 <= ops[1] < 0x10 and 0 <= ops[2] < 0x100
        return np.uint16((ops[0] << 12) | (ops[1] << 8) | ops[2]
        )
    elif len(ops) == 2:
        assert 0 <= ops[0] < 0x10 and 0 <= ops[1] < 0x1000
        return np.uint16(
            (ops[0] << 12) | ops[1]
        )

def reg_tk_int(token : str) -> int:
    """
    Returns the index of a register token.
    """
    assert token in register_mnemonics
    return c16u.to_hex(token[len('r'):])

def dev_tk_int(token : str) -> int:
    """
    Returns the index of a device token.
    """
    assert token in device_mnemonics
    return c16u.to_hex(token[len("dev"):])

class Assembler:
    def __init__(self, src_file, out_file="rom.crm"):
        with open(src_file, 'r') as src:
            self.tokens = tokenise(src.read())
        self.symbol_table = {}
        self.token_index = 0
        self.opcodes = []
        self.out_file = out_file
        self.ctk = self.tokens[self.token_index]

# private implementation functions.

    def next_token(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.ctk = self.tokens[self.token_index]

    def assemble_r2r(self, op1, op2):
        self.token_index += 1
        if self.tokens[self.token_index] not in register_mnemonics:
            raise SyntaxError()
        reg = reg_tk_int(self.tokens[self.token_index])
        self.token_index += 1
        if self.tokens[self.token_index] != ",":
            raise SyntaxError()
        self.token_index += 1
        if self.tokens[self.token_index] not in register_mnemonics:
            raise SyntaxError()
        src = reg_tk_int(self.tokens[self.token_index])
        opcode = build_opcode((op1, reg, src, op2))
        self.opcodes.append(opcode)
        return

    def assemble_cg(self, op1):
        self.token_index += 1
        if self.tokens[self.token_index] in self.symbol_table:
            # Take a copy of the symbol table to prevent an infinite loop
            for t, v in self.symbol_table[self.tokens[self.token_index]][:]:
                if t == "label":
                    # The symbol was encountered earlier in the binary as a jump destination
                    opcode = build_opcode((op1, v))
                    self.opcodes.append(opcode)
                    break
                elif t == "goto":
                    # The symbol was encountered earlier as a goto argument.
                    # Write to the symbol table the location of this goto so that we can fill it in later
                    # when we have an address.
                    self.symbol_table[
                        self.tokens[self.token_index]
                    ].append(
                        ("goto", np.uint16(2*len(self.opcodes)+2))
                    )
                    # Write to memory a blank goto instruction which we will fill out the destination field later.
                    opcode = build_opcode((op1, 0x000))
                    self.opcodes.append(opcode)
                else:
                    # t is a directive, not relevant so do nothing.
                    pass
            return

        else:
            # The symbol will be encountered later.
            # No +2 in this 2*len(self.opcode) as the new opcode not written yet.
            self.symbol_table[self.tokens[self.token_index]] = [("goto", np.uint16(2*len(self.opcodes)))]
            opcode = build_opcode((op1, 0x000))
            self.opcodes.append(opcode)
            return

    def assemble_const(self, op1):
        self.token_index += 1
        if not c16u.is_hex(self.tokens[self.token_index]):
            raise SyntaxError()
        value = int(self.tokens[self.token_index], 16) & 0xFFF
        opcode = build_opcode((op1, value))
        self.opcodes.append(opcode)
        return

    def assemble_dp(self, op):
        self.token_index += 1
        if self.tokens[self.token_index] not in device_mnemonics:
            raise SyntaxError()
        dev = dev_tk_int(self.tokens[self.token_index])
        opcode = build_opcode((0xE, dev, op))
        self.opcodes.append(opcode)
        return
    
    def assemble_drw(self, op1):
        self.token_index += 1
        if self.tokens[self.token_index] not in device_mnemonics:
            raise SyntaxError()
        dev = dev_tk_int(self.tokens[self.token_index])
        self.token_index += 1
        if self.tokens[self.token_index] != ",":
            raise SyntaxError()
        self.token_index += 1
        if not c16u.is_hex(self.tokens[self.token_index]):
            raise SyntaxError()
        const = c16u.to_hex(self.tokens[self.token_index])
        opcode = build_opcode((op1, dev, const))
        self.opcodes.append(opcode)
        return

    def assemble_mem(self, op1, op2):
        self.token_index += 1
        if self.tokens[self.token_index] not in register_mnemonics:
            raise SyntaxError()
        reg = reg_tk_int(self.tokens[self.token_index])
        opcode = build_opcode((op1, reg, op2))
        self.opcodes.append(opcode)
        return
    
    def assemble_rconst(self, op1):
        self.token_index += 1
        if self.tokens[self.token_index] not in register_mnemonics:
            raise SyntaxError()
        reg = reg_tk_int(self.tokens[self.token_index])
        self.token_index += 1
        if self.tokens[self.token_index] != ",":
            raise SyntaxError()
        self.token_index += 1
        if not c16u.is_hex(self.tokens[self.token_index]):
            raise SyntaxError()
        const = c16u.to_hex(self.tokens[self.token_index]) & 0xFF
        opcode = build_opcode((op1, reg, const))
        self.opcodes.append(opcode)
        return
    
    def assemble_shift(self, op1, op2):
        self.token_index += 1
        if self.tokens[self.token_index] not in register_mnemonics:
            raise SyntaxError()
        reg = reg_tk_int(self.tokens[self.token_index])
        self.token_index += 1
        if self.tokens[self.token_index] != ",":
            raise SyntaxError()
        self.token_index += 1
        if not c16u.is_hex(self.tokens[self.token_index]):
            raise SyntaxError()
        src = c16u.to_hex(self.tokens[self.token_index])
        opcode = build_opcode((op1, reg, src, op2))
        self.opcodes.append(opcode)
        return
# public interface
    def assemble_adc(self):
        self.assemble_rconst(0x7)
    
    def assemble_add(self):
        self.assemble_r2r(0x8, 0x4)
    
    def assemble_acr(self):
        self.assemble_rconst(0x6)
    
    def assemble_and(self):
        self.assemble_r2r(0x8, 0x2)

    def assemble_ar(self):
        self.assemble_r2r(0x8, 0x0)
    
    def assemble_bar(self):
        self.assemble_rconst(0xC)

    def assemble_call(self):
        self.assemble_cg(0x2)

    def assemble_cpac(self):
        self.assemble_const(0xB)

    def assemble_db(self):
        self.next_token()
        if not c16u.is_hex(self.ctk):
            raise SyntaxError()
        words = c16u.to_words(c16u.to_hex(self.ctk))
        self.opcodes += words
        return

    def assemble_dpg(self):
        self.assemble_dp(0x01)
    
    def assemble_dps(self):
        self.assemble_dp(0x0)

    def assemble_goto(self):
        self.assemble_cg(0x1)
    
    def assemble_hlt(self):
        self.opcodes.append(np.uint16(0))

    def assemble_label(self):
        if self.tokens[self.token_index] in self.symbol_table:
            # label is referenced by earlier goto or call statement.
            for key, value in self.symbol_table[self.tokens[self.token_index]]:
                if key == "goto":
                    self.opcodes[value >> 1] &= np.uint16(0xF000)
                    if 2*len(self.opcodes) > 0xFFE:
                        raise OverflowError()
                    self.opcodes[value >> 1] |= np.uint16(2*len(self.opcodes))
        else:
            # label is referenced later.
            self.symbol_table[self.tokens[self.token_index]] = [("label", np.uint16(2*len(self.opcodes)))]
        # Skip the ':' character at the end of the label.
        self.token_index += 1

    def assemble_ld(self):
        self.assemble_mem(0xE, 0x65)
    
    def assemble_mpar(self):
        self.assemble_mem(0xE, 0x1E)

    def assemble_or(self):
        self.assemble_r2r(0x8, 0x1)

    def assemble_rdb(self):
        self.assemble_drw(0xF)

    def assemble_ret(self):
        self.opcodes.append(np.uint16(0x1EE))
    
    def assemble_rmp(self):
        self.assemble_mem(0xE, 0x1D)

    def assemble_rsub(self):
        self.assemble_r2r(0x8, 0x7)

    def assemble_shl(self):
        self.assemble_shift(0x8, 0xE)

    def assemble_shr(self):
        self.assemble_shift(0x8, 0x6)

    def assemble_smp(self):
        if c16u.is_hex(self.tokens[self.token_index + 1]):
            self.assemble_const(0xA)
        elif self.tokens[self.token_index + 1].isalnum():
            self.assemble_label_op(0xA)

    def assemble_snec(self):
        self.assemble_rconst(0x3)
    
    def assemble_snuec(self):
        self.assemble_rconst(0x4)

    def assemble_sne(self):
        self.assemble_r2r(0x5, 0x0)
    
    def assemble_snue(self):
        self.assemble_r2r(0x9, 0x0)

    def assemble_spl(self):
        self.assemble_mem(0xE, 0x55)

    def assemble_sub(self):
        self.assemble_r2r(0x8, 0x5)
    
    def assemble_wrb(self):
        self.assemble_drw(0xD)

    def assemble_xch(self):
        self.assemble_r2r(0x8, 0xF)

    def assemble_xor(self):
        self.assemble_r2r(0x8, 0x3)

    def assemble(self):
        opcode_mnemonics = {
            "acr" : self.assemble_acr,
            "adc" : self.assemble_adc,
            "add" : self.assemble_add,
            "and" : self.assemble_and,
            "ar" : self.assemble_ar,
            "bar" : self.assemble_bar,
            "call" : self.assemble_call,
            "cpac" : self.assemble_cpac,
            "db" : self.assemble_db,
            "dpg" : self.assemble_dpg,
            "dps" : self.assemble_dps,
            "goto" : self.assemble_goto,
            "hlt" : self.assemble_hlt,
            "ld" : self.assemble_ld,
            "mpar" : self.assemble_mpar,
            "or" : self.assemble_or,
            "rdb" : self.assemble_rdb,
            "ret" : self.assemble_ret,
            "rmp" : self.assemble_rmp,
            "rsub" : self.assemble_rsub,
            "shl" : self.assemble_shl,
            "shr" : self.assemble_shr,
            "smp" : self.assemble_smp,
            "snec" : self.assemble_snec,
            "snuec" : self.assemble_snuec,
            "sne" : self.assemble_sne,
            "snue" : self.assemble_snue,
            "spl" : self.assemble_spl,
            "sub" : self.assemble_sub,
            "wrb" : self.assemble_wrb,
            "xch" : self.assemble_xch,
            "xor" : self.assemble_xor
        }
        # keep the code length at the beginning of the program code
        # so reserve the slot at the beginning.
        # self.opcodes.append(np.uint16(0))
        while self.token_index < len(self.tokens):
            if self.ctk in opcode_mnemonics:
                opcode_mnemonics[self.ctk]()
            else:
                if self.tokens[self.token_index + 1] == ":":
                    self.assemble_label()
                else:
                    raise SyntaxError()
            self.next_token()
        # self.opcodes[0] = np.uint16(2*len(self.opcodes) - 2)

    def write_out(self):
        with open(self.out_file, "wb") as of:
            for i in self.opcodes:
                of.write(bytearray([np.uint8(c16u.high_byte(i)), np.uint8(c16u.low_byte(i))]))

if __name__ == "__main__":
    assert len(sys.argv) == 3
    ass = Assembler(sys.argv[1], sys.argv[2])
    ass.assemble()
    ass.write_out()