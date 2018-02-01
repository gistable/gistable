from Foundation import NSObject, NSUserDefaults, NSKeyValueObservingOptionNew
from Foundation import NSRunLoop, NSDate


class PrefsObserver(NSObject):
    def observe(self, domain, key):
        self.domain = domain
        self.key = key
        if self:
            self.defaults = NSUserDefaults.alloc().initWithSuiteName_(
                self.domain)
            self.defaults.addObserver_forKeyPath_options_context_(
                self, self.key, NSKeyValueObservingOptionNew, None)
        return self

    def __del__(self):
        self.defaults.removeObserver_forKeyPath_(self, self.key)

    def observeValueForKeyPath_ofObject_change_context_(
            self, keyPath, object, change, context):
        print change


observer = PrefsObserver.alloc().init().observe(
    'ManagedInstalls', 'LastCheckDate')
while True:
    NSRunLoop.currentRunLoop(
        ).runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.3))