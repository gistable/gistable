# Some of this adapted from BoppreH's answer here:http://stackoverflow.com/questions/9817531/applying-low-level-keyboard-hooks-with-python-and-setwindowshookexa
import ctypes
from ctypes import wintypes
from collections import namedtuple


KeyEvents=namedtuple("KeyEvents",(['event_type', 'key_code',
											 'scan_code', 'alt_pressed',
											 'time']))
handlers=[]
def listener():
	"""The listener listens to events and adds them to handlers"""
	from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
	import atexit
	event_types = {0x100: 'key down', #WM_KeyDown for normal keys
				   0x101: 'key up', #WM_KeyUp for normal keys
				   0x104: 'key down', # WM_SYSKEYDOWN, used for Alt key.
				   0x105: 'key up', # WM_SYSKEYUP, used for Alt key.
				  }
	def low_level_handler(nCode, wParam, lParam):
		"""
		Processes a low level Windows keyboard event.
		"""
		event = KeyEvents(event_types[wParam], lParam[0], lParam[1],
						  lParam[2] == 32, lParam[3])
		for h in handlers:
			h(event)
		#Be nice, return next hook
		return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)
	
	# Our low level handler signature.
	CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
	# Convert the Python handler into C pointer.
	pointer = CMPFUNC(low_level_handler)
	#Added 4-18-15 for move to ctypes:
	windll.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
	windll.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
	# Hook both key up and key down events for common keys (non-system).
	
	hook_id = windll.user32.SetWindowsHookExA(0x00D, pointer,
											 windll.kernel32.GetModuleHandleW(None), 0)

	# Register to remove the hook when the interpreter exits.
	atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)
	while True:
		msg = windll.user32.GetMessageW(None, 0, 0,0)
		windll.user32.TranslateMessage(byref(msg))
		windll.user32.DispatchMessageW(byref(msg))
if __name__ == '__main__':
	def print_event(e):
		print e

	handlers.append(print_event)
	listener()