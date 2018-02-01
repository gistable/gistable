import ctypes
import win32net, win32api
import time

current_user = win32api.GetUserNameEx(2)
data = [{"domainandname": current_user}]

def get_members(group_name):
	members = win32net.NetLocalGroupGetMembers(None, group_name, 3)[0]
	print members
	return [x['domainandname'].lower() for x in members]

def is_user_in_group(username, groupname):
	return username.lower() in get_members(groupname)

print 'checking if current user %s has admin rights' % (current_user,)
while True:
	if (is_user_in_group(current_user, 'Administrators')):
		pass # user is already an admin
	else:
		print 'User has been removed from local administrators. Re-adding'
		if (not is_user_in_group(current_user, 'Administrators')):
			win32net.NetLocalGroupAddMembers(None, 'Administrators', 3, data)
			print 'SUCCESS'
		else:
			print 'FAILED'
	time.sleep(10)
