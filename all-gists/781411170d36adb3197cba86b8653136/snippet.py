from binaryninja import (Architecture, RegisterInfo, InstructionInfo,
    InstructionTextToken, InstructionTextTokenType, InstructionTextTokenContext,
    BranchType,
    LowLevelILOperation, LLIL_TEMP,
    LowLevelILLabel,
    FlagRole,
    LowLevelILFlagCondition,
    log_error,
    CallingConvention,
    interaction,
    PluginCommand, BackgroundTaskThread,
    HighlightStandardColor
)


import struct

def hexr(a):
    if a == 0x4:
        return 'UserInput'
    if a == 0x8:
        return 'Output'
    if a == 0xc:
        return 'ReadBool'
    if a == 0x10:
        return 'WriteBool'
    if a == 0x3d00:
        return '*1'
    return hex(a)

# Helper function to make tokens easier to make
def makeToken(tokenType, text, data=None):
    tokenType = {
            'i':InstructionTextTokenType.InstructionToken,
            't':InstructionTextTokenType.TextToken,
            'a':InstructionTextTokenType.PossibleAddressToken,
            's':InstructionTextTokenType.OperandSeparatorToken
    }[tokenType]

    if data is None:
        return InstructionTextToken(tokenType, text)
    return InstructionTextToken(tokenType, text, data)


class Subleq(Architecture):
    name = "subleq"
    address_size = 4
    default_int_size = 4
    max_instr_length = 12 # Each instruction is 3 dwords

    # SP register is required, even if we are not going to use it
    regs = {'sp': RegisterInfo('sp', 2)}
    stack_pointer = 'sp'

    def perform_get_instruction_info(self,data,addr):
        # If we can't decode an instruction return None
        if len(data) < 12:
            return None

        # Unpack our operands from the data
        a,b,c = struct.unpack('<3I',data[:12])

        # Create the InstructionInfo object for our instruction
        res = InstructionInfo()
        res.length = 12

        if c != 0:
            if b == a:
                # Unconditional branch jumps to integer index c
                res.add_branch(BranchType.UnconditionalBranch, c*4)
            else:
                # True branch jumps to integer index c 
                res.add_branch(BranchType.TrueBranch, c*4)
                # False branch continues to next instruction
                res.add_branch(BranchType.FalseBranch, addr + 12)

        return res


    def perform_get_instruction_text(self, data, addr):
        # If we can't decode an instruction return None
        if len(data) < 12:
            return None

        # Unpack our operands from the data
        a,b,c = struct.unpack('<3I',data[:4*3])
        
        tokens = []
        
        # Check for invalid instructions that would crash
        if b*4 >= 0x4400 or a*4 >= 0x4400:
            tokens = []
            tokens.append(makeToken('i', '{:7s}'.format('invalid')))
            return tokens, 4*3

        # Clear instruction to be less verbose
        # clear [B]
        elif a == b:
            tokens = []
            tokens.append(makeToken('i', '{:7s}'.format('clear')))
            tokens.append(makeToken('t', '['))
            tokens.append(makeToken('a', hexr(b*4), b*4))
            tokens.append(makeToken('t', ']'))

        # Normal sub instruction
        # sub [B], [A]
        else:
            tokens.append(makeToken('i', '{:7s}'.format('sub')))
            tokens.append(makeToken('t', '['))


            tokens.append(makeToken('a', hexr(b*4), b*4))
            tokens.append(makeToken('t', ']'))
            tokens.append(makeToken('s', ', '))
            tokens.append(makeToken('t', '['))
            tokens.append(makeToken('a', hexr(a*4), a*4))
            tokens.append(makeToken('t', ']'))

        
        # Unconditional jump
        # ; jmp C
        if c != 0 and b == a:
            tokens.append(makeToken('s', '; '))
            tokens.append(makeToken('i', '{:7s}'.format('jmp')))
            tokens.append(makeToken('a', hex(c*4), c*4))

        # Conditional jump
        # ; jmp C if [B] <= 0
        elif c != 0:
            tokens.append(makeToken('s', '; '))
            tokens.append(makeToken('i', '{:7s}'.format('jmp')))
            tokens.append(makeToken('a', hex(c*4), c*4))
            tokens.append(makeToken('s', ' if '))
            tokens.append(makeToken('t', '['))
            tokens.append(makeToken('a', hex(b*4), b*4))
            tokens.append(makeToken('t', ']'))
            tokens.append(makeToken('t', ' <= 0'))

        return tokens, 4*3


    # Full LLIL lifting for subleq
    def perform_get_instruction_low_level_il(self, data, addr, il):
        # If we can't decode an instruction return None
        if len(data) < 12:
            return None

        # Unpack our operands from the data
        a,b,c = struct.unpack('<3I',data[:4*3])

        # If this instruction would crash, ignore it
        if b*4 >= 0x4400 or a*4 >= 0x4400:
            il.append(il.nop())
            return 4*3

        # A, B, and C as pointers
        addr_a = il.const_pointer(4, a*4)
        addr_b = il.const_pointer(4, a*4)
        addr_c = il.const_pointer(4, c*4)

        # mem[A] and mem[B] pointers
        mem_a = il.load(4, addr_a)
        mem_b = il.load(4, addr_b)

        # For a clear instruction just store 0
        if a == b:
            # *B = 0
            store_b = il.store(4, addr_b, il.const(4,0))
            il.append(store_b)

        # For normal operation, construct a subtraction
        else:
            # *B = *B - *A
            sub_op = il.sub(4, mem_b, mem_a)
            store_b = il.store(4, addr_b, sub_op)
            il.append(store_b)

        # Unconditional jump
        if c != 0 and b == a:
            # goto C
            jmp = il.jump(addr_c)
            il.append(jmp)

        # Conditional jump
        elif c != 0:
            # See if we have marked the True jump target before
            t_target = il.get_label_for_address(Architecture['subleq'],
                    il[il.const_pointer(4, c*4)].constant)

            # Create the False jump label
            f_target = LowLevelILLabel()

            # If we have to create a jump IL for the True target
            indirect = t_target is None
            if indirect:
                t_target = LowLevelILLabel()

            less_op = il.compare_signed_less_equal(4, mem_b, il.const(4, 0))
            if_op = il.if_expr(less_op, t_target, f_target)
            il.append(if_op)

            # We need to create a jump to the true target if it doesn't exist
            if indirect:
                il.mark_label(t_target)
                jmp = il.jump(addr_c)
                il.append(jmp)

            # Last is the fall though for the false target
            il.mark_label(f_target)


        return 12

Subleq.register()



def markModifiableCode(bv, func):
    # Loop over all instructions in the function
    for t in (t for bb in func.basic_blocks for t in bb.disassembly_text):
        # Find our sub tokens
        if not t.tokens[0].text.startswith('sub '):
            continue

        addr = t.tokens[2].value
        # Check if the address is in a basic block
        bbs = bv.get_basic_blocks_at(addr)
        if len(bbs) == 0:
            continue

        # Check that this address really is an instruction
        for tt in bbs[0].disassembly_text:
            if addr - tt.address >= 3 or addr - tt.address < 0:
                continue
            # Highlight it and add comments
            bbs[0].function.set_user_instr_highlight(tt.address,
                    HighlightStandardColor.RedHighlightColor)
            bbs[0].function.set_comment_at(tt.address, "Modified by 0x%x"%t.address)
            func.set_comment_at(t.address, "Modifies code at 0x%x"%tt.address)
            break

PluginCommand.register_for_function('Subleq check modifiable code', 'subleq', markModifiableCode)
