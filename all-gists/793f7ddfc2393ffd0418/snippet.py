##########################################################################
# An IDAPython plugin that generates "comment" for data
#
# Compiler sometimes optimized initialisation of small strings
# and init them with, this example write "Hello!\n":
#     - mov dword ptr[rax + 0], 6c6c6548h
#     - mov dword ptr[rax + 4], a216fh
#
# This plugin will auto comment the following line as:
#     - mov dword ptr[rax + 0], 6c6c6548h; 'Hell'
#     - mov dword ptr[rax + 4], a216fh; 'o\n\x00\x00'
#
# In a second time, you can choose to concatenate them by select both line
# and press "Ctrl+H" or go the Edit menu and click on "Extract selected data"
#
# This will change comment to:
#     - mov dword ptr[rax + 0], 6c6c6548h; 'Hello\n\x00\x00'
#     - mov dword ptr[rax + 4], a216fh;
#
# @BestPig
##########################################################################
import idc
import idaapi
import idautils
import sys


class DataCommentPlugin(idaapi.plugin_t):
    flags = 0
    comment = "Add comment on initialisation data with \"mov dword ptr[reg + 0x10], 74657465h\""
    help = ""
    wanted_name = "DataComment"
    wanted_hotkey = ""

    NAME = "datacomment.py"

    def init(self):
        self.menu_context_extract = idaapi.add_menu_item("Edit/", "Extract selected data", "Ctrl+H", 0, self.dc_extract, (None,))
        idaapi.autoWait()
        for seg_addr in Segments():
            segment = getseg(seg_addr)
            if not segment.perm & SEGPERM_EXEC:
                continue
            self.dcu_extract_between_addr(segment.startEA, segment.endEA)
        return idaapi.PLUGIN_KEEP

    def term(self):
        idaapi.del_menu_item(self.menu_context_extract)
        return None

    def run(self, arg):
        return None

    def dcu_is_wanted_assign(self, instr, addr):
        if instr.get_canon_mnem() != 'mov':
            return False
        if GetOpType(addr, 1) != o_imm:
            return False
        if not getseg(addr).use32():
            return False
        if not 'dword ptr [' in GetOpnd(addr, 0):
            return False
        if (GetOperandValue(addr, 1) & 0xfffff000) == GetOperandValue(addr, 1):
            return False
        return True

    def dcu_extract_between_addr(self, startAddr, endAddr, toMerge=False, force=False):
        current_addr = startAddr
        merged_comment = ''
        first_mov = None
        while current_addr <= endAddr:
            instr = DecodeInstruction(current_addr)
            if not instr:
                current_addr += 1
                continue
            if self.dcu_is_wanted_assign(instr, current_addr):
                if not first_mov:
                    first_mov = current_addr
                data_str = struct.pack('I', GetOperandValue(current_addr, 1) & 0xffffffff)
                if toMerge:
                    merged_comment += data_str
                current_comment = GetCommentEx(current_addr, 1)
                if not current_comment or toMerge or force:
                    exact_comment = repr(data_str)[0 if sys.version_info.major < 3 else 1:]
                    if toMerge and current_comment == exact_comment:
                        MakeRptCmt(current_addr, ' ')
                    elif (not current_comment and not toMerge) or force:
                        MakeRptCmt(current_addr, '%s' % exact_comment)
            current_addr += instr.size
        if merged_comment and first_mov:
            MakeRptCmt(first_mov, '%s' % repr(merged_comment)[0 if sys.version_info.major < 3 else 1:])

    def dc_extract(self, arg):
        multiple, start, end = idaapi.read_selection()
        if multiple:
            self.dcu_extract_between_addr(start, end, True)
        else:
            self.dcu_extract_between_addr(here(), here(), False, True)
        return

def PLUGIN_ENTRY():
    return DataCommentPlugin()
