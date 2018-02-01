#!/usr/bin/env python
from Foundation import NSUserNotification
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotificationDefaultSoundName
from optparse import OptionParser



def main():
    parser = OptionParser(usage='%prog -t TITLE -m MESSAGE')
    parser.add_option('-t', '--title', action='store', default='A title')
    parser.add_option('-m', '--message', action='store', default='...')
    parser.add_option('--no-sound', action='store_false', default=True,
        dest='sound')

    options, args = parser.parse_args()

    notification = NSUserNotification.alloc().init()
    notification.setTitle_(options.title)
    notification.setInformativeText_(options.message)
    if options.sound:
        notification.setSoundName_(NSUserNotificationDefaultSoundName)

    center = NSUserNotificationCenter.defaultUserNotificationCenter()
    center.deliverNotification_(notification)


if __name__ == '__main__':
    main()

