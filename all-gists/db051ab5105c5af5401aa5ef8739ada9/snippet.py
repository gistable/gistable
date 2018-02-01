import time, hou


# version 1. Static class

class SessionCallback(object):
    last_time = time.time()
    interval = 10 # sec

    @classmethod
    def start(cls):
        print 'Callback created'
        # This callback is called approximately every 50ms, unless Houdini is busy processing events.
        hou.ui.addEventLoopCallback(cls.check_timer)

    @classmethod
    def stop(cls):
        print 'Callback deleted'
        hou.ui.removeEventLoopCallback(cls.check_timer)

    @classmethod
    def check_timer(cls):
        if time.time() - cls.last_time > cls.interval:
            cls.last_time = time.time()
            cls.save()

    @classmethod
    def save(cls):
        print 'SAVE'
            
    

hou.session.SaveTimer = SessionCallback
SessionCallback.start()
# SessionCallback.stop()


# version 2. Class instance

class SessionCallback(object):
    interval = 10 # sec

    def __init__(self):
        self.last_time = time.time()

    def start(self):
        print 'Callback created'
        hou.ui.addEventLoopCallback(self.check_timer)

    def stop(self):
        print 'Callback deleted'
        hou.ui.removeEventLoopCallback(self.check_timer)

    def check_timer(self):
        if time.time() - self.last_time > self.interval:
            self.last_time = time.time()
            self.save()

    def save(self):
        print 'SAVE'

hou.session.SaveTimer = SessionCallback()
hou.session.SaveTimer.start()
# hou.session.SaveTimer.stop()
