# python3 required
# tested on Windows 7 & Windows 10

import winreg

try:
	key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
	value = winreg.QueryValueEx(key, "DigitalProductId")
except OSError:
	print(r"""Cannot find value "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DigitalProductId".""")
	quit()
	
assert type(value) is tuple
assert len(value) == 2
if value[1] != 3:
	print(r"""Type mismatch in "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DigitalProductId".""")
	quit()
assert type(value[0]) is bytes

rawdata = list(value[0])
productkey = ""
for i in range(25):
	cur = 0
	for x in range(14, -1, -1):
		cur = rawdata[x + 52] + cur * 256
		rawdata[x + 52] = (cur // 24) & 255
		cur = cur % 24
	productkey = "BCDFGHJKMPQRTVWXY2346789"[cur] + productkey
	if ((i + 1) % 5 == 0) and (i != 24):
		productkey = '-' + productkey

print(productkey)