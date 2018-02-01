# Note: This _will_ GUI prompt a user for permission to locate them via python, even if run as root

from CoreLocation import CLLocationManager, kCLDistanceFilterNone, kCLLocationAccuracyThreeKilometers
from Foundation import NSRunLoop, NSDate, NSObject

is_enabled = CLLocationManager.locationServicesEnabled()
is_authorized = CLLocationManager.authorizationStatus()

class MyLocationManagerDelegate(NSObject):
    def init(self):
        self = super(MyLocationManagerDelegate, self).init()
        if not self:
            return
        self.locationManager = CLLocationManager.alloc().init()
        self.locationManager.setDelegate_(self)
        self.locationManager.setDistanceFilter_(kCLDistanceFilterNone)
        self.locationManager.setDesiredAccuracy_(kCLLocationAccuracyThreeKilometers)
        self.locationManager.startUpdatingLocation()
        return self        
    def locationManager_didUpdateToLocation_fromLocation_(self, manager, newloc, oldloc):
        print "NEW:", newloc.description()
        if oldloc is not None:
            print "OLD:", oldloc.description()
        else:
            print "OLD: <None>"
    def locationManager_didFailWithError_(self, manager, err):
        print "ERR:", err.description()


def main():
    finder = MyLocationManagerDelegate.alloc().init()
    for x in range(5):
         print "loop", x
         NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(10))
