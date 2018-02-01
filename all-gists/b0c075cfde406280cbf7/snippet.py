# coding: utf-8
from objc_util import * 

ObjCClass('NSBundle').bundleWithPath_('/System/Library/Frameworks/LocalAuthentication.framework').load()
context = ObjCClass('LAContext').alloc().init()
policy = 1 #put 1 if you want to auth with password, 2 with passcode
reason = 'We need you fingerprint to ste...ehm... to log you in'

def funct(_cmd,success,error):
	if success:
		print 'Autenticated!'
	else:
		autherr= ObjCInstance(error).localizedDescription()
		
		if str(autherr).startswith('Fallback'):
			if console.input_alert('Password') == 'Itsme':
				print 'Authenticated!'
			else:
				print 'WRONG PSW'
		if str(autherr).startswith('Application retry'):
			print('Wrong Fingerprint!')
		if str(autherr).startswith('Biometry'):
			print('Too many wrong fingerprints!!')
		else:
			print autherr

handler=ObjCBlock(funct,restype=None,argtypes=[c_void_p,c_void_p,c_void_p])
context.evaluatePolicy_localizedReason_reply_(policy,reason,handler)