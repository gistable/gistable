__author__ = 'yeuchimse'

import struct

FileMode = ['rb', 'wb', 'ab', 'r+b', 'w+b', 'a+b']
Registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp']


# region ...
def format_code(v):
    return '[0x%04x]' % v


def format_reg(v):
    return Registers[v]


def format_code_reg(v):
    return '[%s]' % format_reg(v)


def format_value(v):
    return '0x%04x' % v


def uint16(n):
    return n & 0xFFFF


# endregion

# region xtea
def up(s):
    sa = []
    for i in xrange(0, len(s), 4):
        sa.append(struct.unpack('>I', s[i:i + 4])[0])

    return sa


def p(sa):
    s = ''
    for n in sa:
        s += struct.pack('>I', n)

    return s


def xtea_block(c, k):
    v0, v1 = up(c)
    key = up(k)

    delta = 0x9E3779B9
    sum = (delta * 32) & 0xFFFFFFFF
    for i in xrange(32):
        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + key[(sum >> 11) & 3])
        v1 &= 0xFFFFFFFF
        sum -= delta
        sum &= 0xFFFFFFFF
        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + key[sum & 3])
        v0 &= 0xFFFFFFFF

    return p([v0, v1])


# endregion


# region functions
def execute_function_2_params(vm, func):
    print vm.two_params(),

    a, b = vm.code[vm.eip], vm.code[vm.eip + 1]

    type = a >> 6
    if type:
        if type == 1:
            param1 = vm.read_word(a & 0x3F)
        elif type == 2:
            param1 = vm.read_word(vm.regs[a & 0x3F])
    else:
        param1 = vm.regs[a & 0x3F]

    type = b >> 6
    if type:
        if type == 1:
            param2 = vm.read_word(b & 0x3F)
        elif type == 2:
            param2 = vm.read_word(vm.regs[b & 0x3F])
        elif type == 3:
            param2 = b & 0x3F
    else:
        param2 = vm.regs[b & 0x3F]

    result = func(param1, param2)

    type = a >> 6
    if type:
        if type == 1:
            vm.write_word(a & 0x3F, result)
        elif type == 2:
            vm.write_word(vm.regs[a & 0x3F], result)

    else:
        vm.regs[a & 0x3F] = result

    vm.eip += 2


def execute_function_1_param(vm, func):
    print vm.two_params(),
    a = vm.code[vm.eip]

    type = a >> 6
    if type:
        if type == 1:
            param = vm.read_word([a & 0x3F])
            result = func(param)
            vm.write_word(a & 0x3F, result)
        elif type == 2:
            param = vm.read_word([vm.regs[a & 0x3F]])
            result = func(param)
            vm.write_word(vm.regs[a & 0x3F], result)

    else:
        param = vm.regs[a & 0x3F]
        result = func(param)
        vm.regs[a & 0x3F] = result

    if result == 0:
        vm.zero_flag = 1
    else:
        vm.zero_flag = 0

    vm.eip += 1


def add(vm):
    print 'add',
    execute_function_2_params(vm, lambda a, b: a + b)


def sub(vm):
    print 'sub',
    execute_function_2_params(vm, lambda a, b: a - b)


def inc(vm):
    print 'inc',
    execute_function_1_param(vm, lambda a: a + 1)


def dec(vm):
    print 'dec',
    execute_function_1_param(vm, lambda a: a - 1)


def and_(vm):
    print 'and',
    execute_function_2_params(vm, lambda a, b: a & b)


def or_(vm):
    print 'or',
    return execute_function_2_params(vm, lambda a, b: a | b)


def xor(vm):
    print 'xor',
    return execute_function_2_params(vm, lambda a, b: a ^ b)


def not_(vm):
    print 'not',
    execute_function_1_param(vm, lambda a: ~a)


def shl(vm):
    print 'shl',
    return execute_function_2_params(vm, lambda a, b: a << b)


def shr(vm):
    print 'shr',
    return execute_function_2_params(vm, lambda a, b: a >> b)


def rol(vm):
    print 'rol',
    execute_function_2_params(vm, lambda a, b: a << b | a >> (16 - b))


def ror(vm):
    print 'ror',
    execute_function_2_params(vm, lambda a, b: a >> b | a << (16 - b))


def ror8(vm):
    print 'ror8',
    execute_function_1_param(vm, lambda a: a >> 8 | a << 8)


def mov(vm):
    print 'mov',
    execute_function_2_params(vm, lambda a, b: b)


def xtea(vm):
    print 'call xtea'
    num_of_block = vm.code[vm.eip]
    addr = vm.eip + 2

    key = vm.read_bytes(vm.regs[2], 16)
    for i in xrange(num_of_block):
        cipher = vm.read_bytes(addr, 8)
        plain = xtea_block(cipher, key)
        vm.write_bytes(addr, plain)

        addr += 8

    vm.eip += 2


def cmp(vm):
    print 'cmp', vm.two_params(),
    a, b = vm.code[vm.eip], vm.code[vm.eip + 1]

    type = a >> 6
    if type:
        if type == 1:
            param1 = vm.read_word(a & 0x3F)
        elif type == 2:
            param1 = vm.read_word(vm.regs[a & 0x3F])
    else:
        param1 = vm.regs[a & 0x3F]

    type = b >> 6
    if type:
        if type == 1:
            param2 = vm.read_word(b & 0x3F)
        elif type == 2:
            param2 = vm.read_word(vm.regs[b & 0x3F])
        elif type == 3:
            param2 = b & 0x3F
    else:
        param2 = vm.regs[b & 0x3F]

    if param1 - param2 == 0:
        vm.zero_flag = 1
    else:
        vm.zero_flag = 0

    vm.eip += 2


def mul(vm):
    print 'mul',
    a = vm.code[vm.eip]

    type = a >> 6
    if type:
        if type == 1:
            param1 = vm.read_word(a & 0x3F)
        elif type == 2:
            param1 = vm.read_word(vm.regs[a & 0x3F])
    else:
        param1 = vm.regs[a & 0x3F]

    result = vm.regs[0] * param1

    vm.regs[0] = result & 0xFFFF
    vm.regs[3] = (result & 0xFFFF0000) >> 16

    vm.eip += 1


def div(vm):
    print 'div',
    a = vm.code[vm.eip]

    type = a >> 6
    if type:
        if type == 1:
            param = vm.read_word(a & 0x3F)
        elif type == 2:
            param = vm.read_word(vm.regs[a & 0x3F])
    else:
        param = vm.regs[a & 0x3F]

    n = vm.regs[0] | (vm.regs[3] << 16)
    vm.regs[0] = n / param
    vm.regs[3] = n % param

    if vm.regs[0] == 0:
        vm.zero_flag = 1
    else:
        vm.zero_flag = 0

    vm.eip += 1


def xchg(vm):
    print 'xchg', vm.two_params()
    a, b = vm.code[vm.eip], vm.code[vm.eip + 1]

    type2 = b >> 6
    if type2:
        if type2 == 1:
            param2 = vm.read_word(b & 0x3F)
        elif type2 == 2:
            param2 = vm.read_word(vm.regs[b & 0x3F])
    else:
        param2 = vm.regs[b & 0x3F]

    # write dst to src
    type = a >> 6
    if type:
        if type == 1:
            param1 = vm.read_word(a & 0x3F)
            vm.write_word(a & 0x3F, param2)
        elif type == 2:
            param1 = vm.read_word(vm.regs[a & 0x3F])
            vm.write_word(vm.regs[a & 0x3F], param2)
    else:
        param1 = vm.regs[a & 0x3F]
        vm.regs[a & 0x3F] = param2

    # write src to dst
    if type2:
        if type2 == 1:
            vm.write_word(b & 0x3F, param1)
        elif type2 == 2:
            vm.write_word(vm.regs[b & 0x3F], param1)
    else:
        vm.regs[b & 0x3F] = param1

    vm.eip += 2


def call(vm):
    print 'call',
    target = vm.read_word(vm.eip)

    vm.esp -= 1
    vm.eip += 2
    vm.stack[vm.esp] = vm.eip
    vm.eip += target

    print format_value(uint16(vm.eip))


def call_absolute(vm):
    print 'call',
    a = vm.code[vm.eip]

    type = a >> 6
    if type:
        if type == 1:
            param = vm.read_word(a & 0x3F)
        else:
            raise 'Error'
    else:
        param = vm.regs[a & 0x3F]

    vm.esp -= 1
    vm.stack[vm.esp] = vm.eip
    vm.eip = param

    print format_value(uint16(vm.eip))


def ret(vm):
    print 'ret',
    vm.eip = vm.stack[vm.esp]
    vm.esp += 1


def jump(vm):
    print 'jmp',
    vm.eip += vm.read_word(vm.eip) + 2

    print format_value(uint16(vm.eip))


def jump_if_zero(vm):
    print 'jz',
    if vm.zero_flag:
        vm.eip = vm.eip + 2 + vm.read_word(vm.eip)
    else:
        vm.eip += 2

    print format_value(uint16(vm.eip))


def jump_if_not_zero(vm):
    print 'jnz',
    if not vm.zero_flag:
        vm.eip = vm.eip + 2 + vm.read_word(vm.eip)
    else:
        vm.eip += 2

    print format_value(uint16(vm.eip))


def jump_if_error(vm):
    print 'js',
    if vm.error_flag:
        vm.eip = vm.eip + 2 + vm.read_word(vm.eip)
    else:
        vm.eip += 2

    print format_value(uint16(vm.eip))


def jump_if_not_error(vm):
    print 'jns',
    if not vm.error_flag:
        vm.eip = vm.eip + 2 + vm.read_word(vm.eip)
    else:
        vm.eip = vm.eip + 2

    print format_value(uint16(vm.eip))


def loop(vm):
    print 'loop',
    vm.regs[2] -= 1
    if vm.regs[2]:
        vm.eip = vm.eip + 2 + vm.read_word(vm.eip)
    else:
        vm.eip = vm.eip + 2

    print format_value(uint16(vm.eip))


def read_from(vm):
    print 'mov %s, %s' % (format_reg(0), format_code_reg(4))
    print '        inc %s' % (format_reg(4)),

    vm.regs[0] = vm.code[vm.regs[4]]
    if vm.flags & 0b1000000 == 0:
        vm.regs[4] += 1
    else:
        vm.regs[4] -= 1


def write_to(vm):
    print 'mov %s, %s' % (format_code_reg(5), format_reg(0))
    print '        inc %s' % (format_reg(5)),

    vm.code[vm.regs[5]] = vm.regs[0]
    if vm.flags & 0b1000000:
        vm.regs[5] -= 1
    else:
        vm.regs[5] += 1


def push(vm):
    print 'push', vm.one_param(),
    a = vm.code[vm.eip]

    type = a >> 6
    if type:
        if type == 1:
            param = vm.read_word(a & 0x3F)
        elif type == 2:
            param = vm.read_word(vm.regs[a & 0x3F])

    else:
        param = vm.regs[a & 0x3F]

    vm.esp -= 1
    vm.stack[vm.esp] = param
    vm.eip += 1


def pop(vm):
    print 'pop', vm.one_param(),
    value = vm.stack[vm.esp]
    vm.esp += 1

    a = vm.code[vm.eip]
    type = a >> 6
    if type:
        if type == 1:
            vm.write_word(a & 0x3F, value)
        elif type == 2:
            vm.write_word(vm.regs[a & 0x3F], value)

    else:
        vm.regs[a & 0x3F] = value

    vm.eip += 1


def open_file(vm):
    filename = vm.read_str(vm.regs[3])
    filemode = FileMode[vm.regs[2]]

    print 'open(%r, %r)' % (filename, filemode),

    try:
        vm.files[0] = open(filename, filemode)
        vm.error_flag = 0
    except:
        vm.error_flag = 1


def close_file(vm):
    print 'close',
    vm.error_flag = 0


def read_char(vm):
    print 'fgetc',
    vm.flags &= 0b11111110
    vm.regs[0] = ord(vm.files[0].read(1))


def print_char(vm):
    print 'print %r' % chr(vm.regs[2] & 0xFF),

    vm.stdout += chr(vm.regs[2] & 0xFF)


def finish():
    print 'finish'
    pass


def clear_flags_6(vm):
    vm.flags &= 0b10111111


def set_flags_6(vm):
    vm.flags |= 0b01000000


def null(vm):
    print 'nop',


def exit(vm):
    print 'exit',
    vm.finish = 1


def process_first_block(vm):
    print 'call process_first_block'
    a = vm.code[vm.eip]
    print '        div %s, 0x%x' % (format_reg(a % 0x3F), 11)

    v = vm.regs[a % 0x3F]
    vm.regs[0] = v / 11
    vm.regs[3] = v % 11
    if v:
        vm.zero_flag = 0
    else:
        vm.zero_flag = 1

    vm.eip += 1


def process_second_block(vm):
    print 'call process_second_block'
    a = vm.code[vm.eip]
    print '        div %s, 0x%x' % (format_reg(a % 0x3F), 9)

    v = vm.regs[a % 0x3F]
    vm.regs[0] = v / 9
    vm.regs[3] = v % 9
    if v:
        vm.zero_flag = 0
    else:
        vm.zero_flag = 1

    vm.eip += 1


# endregion


# region VM
class VM(object):
    def __init__(self):
        self.regs = [0] * 8
        self.esp = 256
        self.flags = 0
        self.eip = 0
        self.files = [None] * 20
        self.error_code = 0
        self.functions = [None] * 43
        self.instrutions = {}
        self.finish = 0
        self.stdout = ''

        self.code = open('code.hex', 'rb').read().decode('hex')
        self.code = map(ord, self.code)

        self.code_word = []
        for i in xrange(0, len(self.code), 2):
            a, b = self.code[i], self.code[i + 1]
            self.code_word.append(a | (b << 16))

        self.stack = [0] * 256
        self.code_size = 980
        self.buf_size = 2004

        self.functions[0] = add
        self.functions[1] = sub
        self.functions[2] = cmp
        self.functions[3] = mul
        self.functions[4] = div
        self.functions[5] = inc
        self.functions[6] = dec
        self.functions[7] = and_
        self.functions[8] = or_
        self.functions[9] = xor
        self.functions[10] = not_
        self.functions[11] = mov
        self.functions[12] = xchg
        self.functions[13] = ror8
        self.functions[14] = shl
        self.functions[15] = shr
        self.functions[16] = rol
        self.functions[17] = ror
        self.functions[18] = loop
        self.functions[19] = read_from
        self.functions[20] = write_to
        self.functions[21] = push
        self.functions[22] = pop
        self.functions[23] = xtea
        self.functions[24] = call
        self.functions[25] = call_absolute
        self.functions[26] = ret
        self.functions[27] = jump
        self.functions[28] = jump_if_zero
        self.functions[29] = jump_if_not_zero
        self.functions[30] = jump_if_error
        self.functions[31] = jump_if_not_error
        self.functions[32] = open_file
        self.functions[33] = close_file
        self.functions[34] = read_char
        self.functions[35] = print_char
        self.functions[36] = exit
        self.functions[37] = exit
        self.functions[38] = clear_flags_6
        self.functions[39] = set_flags_6
        self.functions[40] = null
        self.functions[41] = process_first_block
        self.functions[42] = process_second_block

    def read_word(self, i):
        return self.code[i] | (self.code[i + 1] << 8)

    def write_word(self, i, value):
        self.code[i] = value & 0xFF
        self.code[i + 1] = (value & 0xFF00) >> 8

    def read_str(self, i):
        return ''.join(map(chr, self.code[i:])).split('\x00')[0]

    def read_bytes(self, i, n):
        return ''.join(map(chr, self.code[i:]))[:n]

    def write_bytes(self, i, s):
        s = map(ord, s)
        for j in xrange(len(s)):
            self.code[i + j] = s[j]

    def two_params(self):
        param1, param2 = self.code[vm.eip], self.code[vm.eip + 1]

        type1 = param1 >> 6
        if type1:
            if type1 == 1:
                src = format_code(param1 & 0x3F)
            elif type1 == 2:
                src = format_code_reg(param1 & 0x3F)
        else:
            src = format_reg(param1 & 0x3F)

        try:
            type2 = param2 >> 6
            if type2:
                if type2 == 1:
                    dst = format_code(param2 & 0x3F)
                elif type2 == 2:
                    dst = format_code_reg(param2 & 0x3F)
                elif type2 == 3:
                    dst = format_value(param2 & 0x3F)
            else:
                dst = format_reg(param2 & 0x3F)

            return '%s, %s' % (src, dst)
        except:
            return '%s' % src

    def one_param(self):
        param1 = self.code[vm.eip]

        type1 = param1 >> 6
        if type1:
            if type1 == 1:
                src = format_code(param1 & 0x3F)
            elif type1 == 2:
                src = format_code_reg(param1 & 0x3F)
        else:
            src = format_reg(param1 & 0x3F)

        return '%s' % src

    def registers(self):
        return 'eax: 0x%04x | ebx: 0x%04x | ecx: 0x%04x | edx: 0x%04x \n' \
               '       esi: 0x%04x | edi: 0x%04x | esp: 0x%04x | ebp: 0x%04x' % tuple(
            self.regs)

    @property
    def error_flag(self):
        return self.flags & 1

    @error_flag.setter
    def error_flag(self, v):
        if v:
            self.flags |= 1
        else:
            self.flags &= 0b11111110

    @property
    def zero_flag(self):
        return (self.flags & 0b1000) >> 3

    @zero_flag.setter
    def zero_flag(self, v):
        if v:
            self.flags |= 0b1000
        else:
            self.flags &= 0b11110111

    @property
    def esp(self):
        return self.regs[6]

    @esp.setter
    def esp(self, v):
        self.regs[6] = v

    def run(self):
        while self.eip < self.code_size:
            print ''

            function_index = self.code[self.eip]
            if function_index > 43:
                return

            self.eip += 1

            if self.eip not in self.instrutions:
                self.instrutions[self.eip] = True

            print 'regs : ', self.registers()
            print 'stack: ', map(hex, vm.stack[-5:][::-1])
            print 'flag :  %s (zero flag: %d | error_flag: %d)' % (bin(vm.flags), vm.zero_flag, vm.error_flag)
            print '0x%04x ' % (self.eip - 1), # because now eip already points to next instruction
            self.functions[function_index](self)
            print ''

            self.eip = uint16(self.eip)
            self.regs = map(uint16, self.regs)

            if vm.finish:
                break

        print vm.stdout


# endregion


vm = VM()
vm.run()
