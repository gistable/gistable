# Slide : https://docs.google.com/presentation/d/1jLUDucNtvGotHw0LOvDonMYwCkXYcb-cnsOWLNt-Ag0
import sys
import pefile
from capstone import *
from capstone.x86 import *
from keystone import *
from datetime import datetime

MAX_DISASM_COUNT = 1000 * 1000
FILE_NAME = r"dump-g4pic.dll"

walked_branch = []
begin = datetime.now()

def is_branch(mnemonic):
    return mnemonic.upper() in ["JA", "JAE", 'JB', 'JBE', 'JC', 'JCXZ', 'JECXZ', 'JRCXZ', "JE", "JG", "JGE", "JL",
                                "JLE", "JNA", "JNAE", "JNB", "JNBE", "JNC", "JNE", "JNG", "JNGE", "JNL", "JNLE", "JNO",
                                "JNP", "JNS", "JNZ", "JO", "JP", "JPE", "JPO", "JS", "JZ"]


def patch(image, image_base, address, patch_data):
    i = 0
    for b in patch_data:
        image[address - image_base + i] = b
        i += 1


def patch_code(image, image_base, address, assembly):
    ks = Ks(KS_ARCH_X86, KS_MODE_32)
    encoding, _ = ks.asm(assembly, address)
    patch_data = ''.join(chr(e) for e in encoding)
    return patch(image, image_base, address, patch_data)


def detect(insn1, insn2, address):
    if insn1.mnemonic == 'ret':
            return 0, 0, 0

    elif insn1.mnemonic == 'jmp' and insn1.operands[0].type == X86_OP_IMM and (insn1.size == 5 or insn1.size == 2):
        return insn1.operands[0].imm, 0, 0

    elif (insn1.size == 5 and insn1.mnemonic == 'push' and insn1.operands[0].type == X86_OP_IMM) and (
                    insn2.size == 1 and insn2.mnemonic == 'ret'):
        return insn1.operands[0].imm, 0, 6

    elif ((insn1.size == 6 and insn1.mnemonic in ['jz', 'je'] and insn2.size == 6 and insn2.mnemonic in ['jnz', 'jne']) \
        or (insn1.size == 6 and insn1.mnemonic in ['jnz', 'jne'] and insn2.size == 6 and insn2.mnemonic in ['jz', 'je'])) \
        and (insn1.operands[0].type == X86_OP_IMM and insn2.operands[0].type == X86_OP_IMM and insn1.operands[0].imm == insn2.operands[0].imm):
        return insn1.operands[0].imm, 0, 12

    elif is_branch(insn1.mnemonic):
        return address + insn1.size, insn1.operands[0].imm, 0

    elif insn1.mnemonic == 'call' and insn1.size == 5 and insn1.operands[0].type == X86_OP_IMM:
        return address + insn1.size, insn1.operands[0].imm, 0
    else:
        return address + insn1.size, 0, 0


def deobfuscate_an_instruction(image, image_base, address):
    try:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True

        code = image[address - image_base: address - image_base + 32]
        try:
            insns = md.disasm(str(code), address, 2)
            insn1 = insns.next()
            insn2 = insns.next()
            insns.close()
        except StopIteration:
            return 0, 0
        new_address, branch, patch_size = detect(insn1, insn2, address)
        if patch_size > 0:
            assembly = 'jmp 0x%08x' % new_address
            patch_code(image, image_base, address, assembly)
            patch(image, image_base, address + 5, (patch_size - 5) * '\x90')
            print "[+] 0x%x:\t%08s\t%s" % (insn1.address, insn1.mnemonic, insn1.op_str), '-->', assembly

        return new_address, branch

    except Exception as e:
        print '[+] [Exception]:', e
    return 0, 0


def deobfuscate(image, image_base, address):
    """

    :rtype : list
    """
    global walked_branch
    count = 0
    branch_list = []
    if address == 0: return branch_list

    print ('[+] Start analysing at 0x{:08x}'.format(address))
    while address > 0:

        if MAX_DISASM_COUNT > 0 and count >= MAX_DISASM_COUNT:
            break
        walked_branch.append(address)
        address, branch = deobfuscate_an_instruction(image, image_base, address)
        if count > 0 and count % (MAX_DISASM_COUNT / 10) == 0:
            print ('[.] Still working.. {} at 0x{:08x}'.format(datetime.now() - begin, address))
        count += 1
        if address in walked_branch:
            if not branch_list:  # branch list is empty
                break
            address = branch_list.pop(0)
            print ('[+] Switch to branch 0x{:08x}'.format(address))
            continue

        if address == 0:
            if not branch_list:  # branch list is empty
                break
            else:
                address = branch_list.pop(0)
                print ('[+] Switch to branch 0x{:08x}'.format(address))
                walked_branch.append(address)

        if (branch != 0) and (branch not in branch_list) and (branch not in walked_branch):
            branch_list.append(branch)

    if not branch_list:
        print ('[+] Finish branch 0x{:08x}'.format(address))

    return branch_list


def detect_prologue(image, image_base, min_va):
    index = min_va
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True

    prologue_list = []
    while True:
        if index > len(image):
            break
        found = image[index:].find('\x55')
        if found == -1:
            break

        original_address = index + found
        index += found + 1

        address = original_address+1
        for i in range(50):
            code = image[address: address + 32]
            try:
                insns = md.disasm(str(code), image_base + index, 2)
                insn1 = insns.next()
                insn2 = insns.next()
                insns.close()
            except StopIteration:
                break
            except CsError as ex:
                print("ERROR: %s" % ex)
                break

            if insn1.mnemonic == u'mov' and insn1.op_str == u'ebp, esp':
                prologue_list.append(original_address + image_base)
                break
            address, _, _ = detect(insn1, insn2, address+ image_base)
            address -= image_base

    return prologue_list


def deobfuscate_malware(pe, memory_mapped_image, image_base, start_address=0):
    if start_address == 0:
        # find all addresses
        min_va = 0xffffffff
        for section in pe.sections:
            VirtualAddress_adj = pe.adjust_SectionAlignment(section.VirtualAddress,
                                                            pe.OPTIONAL_HEADER.SectionAlignment,
                                                            pe.OPTIONAL_HEADER.FileAlignment)
            min_va = min(min_va, VirtualAddress_adj)

        print ('[+] Finding prologue ...')
        prologue_list = detect_prologue(memory_mapped_image, image_base, min_va)
        print ('[+] Start deobfuscating ...')
        for prologue in prologue_list:
            branch_list = deobfuscate(memory_mapped_image, image_base, prologue)
            while branch_list:
                address = branch_list.pop(0)
                branch_list += deobfuscate(memory_mapped_image, image_base, address)

    else:
        branch_list = deobfuscate(memory_mapped_image, image_base, start_address)
        while branch_list:
                address = branch_list.pop(0)
                branch_list += deobfuscate(memory_mapped_image, image_base, address)


    for section in pe.sections:
        VirtualAddress_adj = pe.adjust_SectionAlignment(section.VirtualAddress,
                                                        pe.OPTIONAL_HEADER.SectionAlignment,
                                                        pe.OPTIONAL_HEADER.FileAlignment)
        if section.Misc_VirtualSize == 0 or section.SizeOfRawData == 0:
            continue
        if section.SizeOfRawData > len(memory_mapped_image):
            continue
        if pe.adjust_FileAlignment(section.PointerToRawData, pe.OPTIONAL_HEADER.FileAlignment) > len(memory_mapped_image):
            continue

        pe.set_bytes_at_rva(VirtualAddress_adj, bytes(memory_mapped_image[ VirtualAddress_adj: VirtualAddress_adj + section.SizeOfRawData]))

def main():
    print ('[+] Parse PE file')
    pe = pefile.PE(FILE_NAME, fast_load=True)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    address_of_entry_point = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    print ('[+] Map PE file')
    memory_mapped_image = bytearray(pe.get_memory_mapped_image())
    deobfuscate_malware(pe, memory_mapped_image, image_base)#image_base + address_of_entry_point)

    print ('[+] Save to file {}'.format(FILE_NAME + '.cleaned'))
    pe.write(FILE_NAME + '.cleaned')
    print ('[+] Total time spent deobfuscating file: {}'.format(datetime.now() - begin))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print 'Exception', e