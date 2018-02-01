__author__ = "Arun K Rajeevan (kra3)"
__copyright__ = "Copyright 2011-2012"
__license__ = "BSD"
__version__ = "2"
__email__ = "the1.arun@gmail.com"
__status__ = "Production"

import time
import ctypes

class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_ulong), ('y', ctypes.c_ulong)]
    
u32 = ctypes.windll.user32
global pt
pt = POINT()

if __name__ == "__main__":
    while True:
        for i in range(27):
            u32.GetCursorPos(ctypes.byref(pt))        
            x = int(pt.x+1)
            y = int(pt.y+1)
            u32.SetCursorPos(x,y)
            time.sleep(3.33)
        u32.mouse_event(4, x, y, 0,0)

