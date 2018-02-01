# hotkey_utils.py - bNull
# 
# Some useful shortcuts for binding to hotkeys. Current output/hotkeys:
#
# [+] Bound make_dwords to Ctrl-Alt-D
# [+] Bound make_cstrings to Ctrl-Alt-A
# [+] Bound make_offset to Ctrl-Alt-O

import idaapi
import idc
import inspect

def selection_is_valid(selection, ea):
    """If the cursor is not at the beginning or the end of our selection, assume that
    something bad has gone wrong and bail out instead of turning a lot of important
    things into dwords.
    """
    if not (ea == selection[1] or ea == selection[2]-1):
        return False
    else:
        return True

def cool_to_clobber(ea):
    """Verify whether or not the byte is somethng that we'll regret clobbering at 
    some later point
    """
    # Currently, just check to see if there's an instruction defined there. 
    # TODO: Check for additional things would not be cool-to-clobber.
    if idc.GetMnem(ea):
        return False
    else:
        return True

def get_selected_bytes():
    """Highlight a range and turn it into dwords
    
    NOTE: read_selection appears to be a fickle bitch. You absolutely have to 
    select more than one line at a time in order for it to work as expected.
    """
      
    selected = idaapi.read_selection()
    curr_ea = idc.ScreenEA()
    print "[+] Processing range: %x - %x" % (selected[1],selected[2])
    
    # refer to selection_is_valid comments regarding the need for this check 

    if (selection_is_valid(selected, curr_ea)):
        return selected
    else:
        return None

def make_dwords():
    selected = get_selected_bytes()
    if selected:
        for ea in range(selected[1], selected[2], 4):
            if not cool_to_clobber(ea):
                print "[-] Error: Something that we shouldn't clobber at 0x%x" % ea
                break
            idaapi.doDwrd(ea,4)
            print "[+] Processed %x" % ea
    else:
        print "[-] Error: EA is not currently a selection endpoint %x" % idc.ScreenEA()

def make_cstrings():
    """Highlight a range and turn it into c-style strings
    
    NOTE: read_selection appears to be a fickle bitch. You absolutely have to 
    select more than one line at a time in order for it to work as expected.
    """
    # TODO check to verify that each byte is valid ascii
    selected = get_selected_bytes()
    if selected:
        curr_start = selected[1]
        curr_length = 0
        for ea in range(selected[1], selected[2]):
            if not cool_to_clobber(ea):
                print "[-] Error: Something that we shouldn't clobber at 0x%x" % ea
                break
            curr_byte = idaapi.get_byte(ea)
            curr_length += 1
            if curr_byte == 0:
                if curr_length > 1:
                    idaapi.doASCI(curr_start,curr_length)
                    curr_length = 0
                    curr_start = ea + 1
                else:
                    curr_length = 0
                    curr_start = ea + 1
    else:
        print "[-] Error: EA is not currently a selection endpoint %x" % idc.ScreenEA()

def make_offset():
    """Resolve an offset to a pointer
    
    For some reason, it seems as though IDA will not auto-define a pointer DWORD. Ex:
    
       .rodata:08E30000                 dd 8271234h
    
    In the case that 0x8271234 is actually a function, resolving the offset will 
    result in:
    
       .rodata:08E30000                 dd offset _ZN29ClassAD1Ev ; ClassA::~ClassA()
    """
    idc.OpOffset(idc.ScreenEA(),0)

def load_hotkeys():
    ENABLED_HOTKEYS = [
            ("Ctrl-Alt-D", make_dwords),
            ("Ctrl-Alt-A", make_cstrings),
            ("Ctrl-Alt-O", make_offset)
            ]

    for func in ENABLED_HOTKEYS:
        func_name = inspect.getmembers(func[1])[-1][1]
        if idaapi.add_hotkey(func[0], func[1]):
            print "[+] Bound %s to %s" % (func_name, func[0])
        else:
            print "[-] Error: Unable to bind %s to %s" % (func_name, func[0])

load_hotkeys()