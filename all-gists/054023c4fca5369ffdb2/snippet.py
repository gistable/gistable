import os
import idaapi
import idautils
import clipboard

def copy_windbg_bp():
    bp = 'bu @!"{}"+0x{:X}'.format(
        os.path.splitext(idaapi.get_root_filename())[0],
        idaapi.get_screen_ea() - idautils.peutils_t().imagebase
        )
    clipboard.copy(bp)

idaapi.add_hotkey('3', copy_windbg_bp)