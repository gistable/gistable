# Update: This looks like a far better solution...
# `console.set_idle_timer_disabled(flag)`
# Disable or enable the idle timer (which puts the device to sleep after a certain period of inactivity).

# noDoze.py -- keep relaunching yourself to prevent
#              your iOS device from falling asleep.
 
import notification, time, urllib
 
def argsString(argv):
    if len(argv) < 2:  # args for first time thru
    	argv = [None, 0, "This is only a test..."]
    argv[1] = int(argv[1]) + 1
    if argv[1] > 15:   # stop after 15 lifetimes!
    	sys.exit()
    argStr = ''
    for arg in argv[1:]:  # ignore argv[0]
	    argStr += '&' + urllib.urlencode({'argv' : arg})
    return argStr
 
def reincarnate(argv):  # relaunch self with state in args
    (theMessage, theSound) = ('', '')  # Silent notification
    theDelay = 1  # Just one second of downtime
    thisScript = sys.argv[0].rpartition('/')[2].partition('.')[0]
    actionURL = 'pythonista://{}?action=run{}'
    actionURL = actionURL.format(thisScript, argsString(argv))
    returnCode = notification.schedule(theMessage, theDelay,
                                       theSound, actionURL)
    #print(returnCode['action_url'])
 
def main(argv):
    print('main({}) -- Going to sleep for 30 seconds...'.format(argv[1:]))
    time.sleep(30)     # Sleep for 30 seconds.
    reincarnate(argv)  # Silent notification can relaunch self
 
if __name__ == '__main__':
    main(sys.argv)
