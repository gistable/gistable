from ctypes import CDLL

loginPF = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
result = loginPF.SACLockScreenImmediate()
