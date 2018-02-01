# Uses PyWin32 http://timgolden.me.uk/pywin32-docs/win32clipboard.html
import win32clipboard

def get_clipboard():
	win32clipboard.OpenClipboard()
	data = win32clipboard.GetClipboardData()
	win32clipboard.CloseClipboard()
	return data

def set_clipboard(text):
	win32clipboard.OpenClipboard()
	win32clipboard.EmptyClipboard()
	win32clipboard.SetClipboard(text.encode('utf-8'),
					win32clipboard.CF_TEXT)
	win32clipboard.SetClipboard(unicode(text),
					win32clipboard.CF_UNICODETEXT)
	win32clipboard.CloseClipboard()
