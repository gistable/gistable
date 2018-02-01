#!/usr/bin/python

import grp, pwd, os
from ctypes import *
from ctypes.util import find_library

libc = cdll.LoadLibrary(find_library('libc'))

# getgrouplist_2() is an undocumented API which, I beleive, retrives all of
# a user's groups instead of the maximum 16 groups which getgrouplist() gets
getgrouplist_2 = libc.getgrouplist_2
# from: http://opensource.apple.com/source/shell_cmds/shell_cmds-116/id/id.c
# .. and: https://opensource.apple.com/source/OpenSSH/OpenSSH-195/openssh/groupaccess.c
# .. and: http://opensource.apple.com//source/samba/samba-235/patches/add-ds-groups-to-token
# // SPI for 5235093
# int32_t getgrouplist_2(const char *, gid_t, gid_t **);
getgrouplist_2.argtypes = [c_char_p, c_uint, POINTER(POINTER(c_uint))]
getgrouplist_2.restype = c_int32

grouplist = POINTER(c_uint)()

user_id = os.getuid() # "username"

user = pwd.getpwuid(user_id)

ct = getgrouplist_2(user.pw_name, user.pw_gid, byref(grouplist))

for i in xrange(0, ct):
	gid = grouplist[i]

	print grp.getgrgid(gid).gr_name
