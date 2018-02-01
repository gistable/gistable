# 
# Callback when the user click on a register
#

from idaapi import *

def extract_reg(line, cx):
    linelen = len(line)
    if cx >= linelen:
        return

    walker_cx = 0
    byte_idx = 0
    last_reg_start_idx = None
    while walker_cx <= cx and byte_idx < linelen:
        cur = line[byte_idx]
        # print "byte_idx=%d, walker_cx=%d, cur=%d (%s)" % (byte_idx, walker_cx, ord(cur), "N/A" if ord(cur) < 32 or ord(cur) > 122 else cur)
        if cur == COLOR_ON:
            if ord(line[byte_idx + 1]) == COLOR_REG:
                last_reg_start_idx = byte_idx + 2
            byte_idx += 2
        elif cur == COLOR_OFF:
            if ord(line[byte_idx + 1]) == COLOR_REG:
                last_reg_start_idx = None
            byte_idx += 2
        else:
            byte_idx += 1
            walker_cx += 1

    if last_reg_start_idx:
        last_reg_end_idx = last_reg_start_idx
        while line[last_reg_end_idx] != COLOR_OFF and last_reg_end_idx < linelen:
            last_reg_end_idx += 1
        return line[last_reg_start_idx:last_reg_end_idx]


class MyWrapper(IDAViewWrapper):
    def __init__(self, title):
        IDAViewWrapper.__init__(self, title)

    def OnViewClick(self, px, py, state):
        widget = pycim_get_tcustom_control(self)

        from_mouse = False 
        
        # get current line
        line = get_custom_viewer_curline(widget, from_mouse)

        # get current X, Y in rows&columns space (as opposed to pixel space)
        _, cx, cy = get_custom_viewer_place(widget, from_mouse)

        reg = extract_reg(line, cx)
        if reg:
            print "Register: '%s'" % reg


W = MyWrapper("IDA View-A")
if not W.Bind():
    print "Binding failed!"