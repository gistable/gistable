# Banner-style (default)
from Foundation import NSUserNotification, NSUserNotificationCenter
def notify(title, subtitle, text):
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(str(title))
    notification.setSubtitle_(str(subtitle))
    notification.setInformativeText_(str(text))
    notification.setSoundName_("NSUserNotificationDefaultSoundName")
    NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

# Usage for this style:
notify(...)


# For Alert-style (but has to be changed in Notification Center after first notification)
from Foundation import NSUserNotification, NSUserNotificationCenter, NSObject
class Notification(NSObject):
    def notify(self, title, subtitle, text, url):
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(str(title))
        notification.setSubtitle_(str(subtitle))
        notification.setInformativeText_(str(text))
        notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setUserInfo_({"action":"open_url", "value":url})
        NSUserNotificationCenter.defaultUserNotificationCenter().setDelegate_(self)
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)
    def userNotificationCenter_didActivateNotification_(self, center, notification):
        userInfo = notification.userInfo()
        # Do something with it

# Usage for this style:
notify_obj = Notification.alloc().init()
notify_obj.notify(...)


# Credit to: http://stackoverflow.com/questions/12202983/working-with-mountain-lions-notification-center-using-pyobjc