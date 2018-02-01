import Foundation
import objc
import AppKit
import sys

NSUserNotification = objc.lookUpClass('NSUserNotification')
NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')

def notify(title, subtitle, info_text, delay=0, sound=False, userInfo={}):
	notification = NSUserNotification.alloc().init()
	notification.setTitle_(title)
	notification.setSubtitle_(subtitle)
	notification.setInformativeText_(info_text)
	notification.setUserInfo_(userInfo)
	if sound:
		notification.setSoundName_("NSUserNotificationDefaultSoundName")
	notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(delay, Foundation.NSDate.date()))
	NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)


notify("Test message", "Subtitle", "This message should appear instantly, with a sound", sound=True)
sys.stdout.write("Notification sent...\n")

