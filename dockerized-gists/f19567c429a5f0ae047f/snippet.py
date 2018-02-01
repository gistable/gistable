#!/usr/bin/python

# Put a background in the same directory as this .py file and name it
backdrop_filename = "backdrop.jpg"

# http://wallreborn.com/wp-content/uploads/2015/05/cool-desktop-backgrounds-8-Cool-Wallpaper.jpg
# is a pretty sweet example to try with

# Then run this script from the Terminal :)

import multiprocessing, time, os.path

def show_backdrop(comm_queue, image_path):
    from AppKit import NSWindow, NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorStationary, \
                       NSWindowCollectionBehaviorIgnoresCycle, NSBorderlessWindowMask, NSBackingStoreBuffered, NSColor, \
                       NSApplication, NSScreen, NSView, NSImage, NSImageView, NSZeroRect, NSCompositeCopy, NSApp, \
                       NSTimer, NSObject, NSEvent, NSApplicationDefined, NSMakePoint, NSBundle
    from Quartz import kCGDesktopWindowLevel
    from ctypes import CDLL, Structure, POINTER, c_uint32, byref
    from ctypes.util import find_library
    class ProcessSerialNumber(Structure):
        _fields_    = [('highLongOfPSN', c_uint32),
                       ('lowLongOfPSN',  c_uint32)]
    kCurrentProcess = 2
    kProcessTransformToUIElementAppication = 4
    ApplicationServices           = CDLL(find_library('ApplicationServices'))
    TransformProcessType          = ApplicationServices.TransformProcessType
    TransformProcessType.argtypes = [POINTER(ProcessSerialNumber), c_uint32]
    class MainController(NSObject):
        timer = None
        def kickRunLoop(self):
            event = NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(NSApplicationDefined, \
                            NSMakePoint(0,0), 0, 0.0, 0, None, 0, 0, 0)
            NSApp.postEvent_atStart_(event, True)
        def checkProcess_(self, timer):
            if not comm_queue.empty():
                # We Get Signal, Take Off Every Zig - er, time to shut down this forked process
                # Clear the queue
                while not comm_queue.empty():
                    ignore = comm_queue.get_nowait()
                NSApp.stop_(None)
                # After you stop the runloop, the app has to receive another event to determine the runloop stopped ...
                self.kickRunLoop()
        def run(self):
            # You could adjust the 1.0 here to how ever many seconds you wanted to wait between checks to terminate
            self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(1.0, self, self.checkProcess_, None, True)
            NSApp.run()
    class FullScreenWindow(NSWindow):
        def canBecomeKeyWindow(self):
            return False
        def canBecomeMainWindow(self):
            return False
    class LockView(NSView):
        def getTopOffset(self, height):
            return (self.bounds().size.height / 2) - height / 2
        def getLeftOffset(self, width):
            return (self.bounds().size.width / 2) - width / 2
        def drawRect_(self, rect):
            image = NSImage.alloc().initWithContentsOfFile_(image_path)
            rep = image.representations()[0]
            bg_width = rep.pixelsWide()
            bg_height = rep.pixelsHigh()
            image.drawInRect_fromRect_operation_fraction_(((self.getLeftOffset(bg_width), self.getTopOffset(bg_height)), (bg_width, bg_height)), NSZeroRect, NSCompositeCopy, 1.0)
            imageView = NSImageView.alloc().init()
            imageView.setImage_(image)
            self.addSubview_(imageView)
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    # Did you know you can override parts of infoDictionary (Info.plist, after loading) even though Apple says it's read-only?
    # This is enough to make an app faceless / without a Dock icon
    info['LSUIElement'] = '1'
    # Initialize our shared application instance
    app = NSApplication.sharedApplication()
    # ... This isn't really necessary, but it's nice to ensure that the application truly is UIElement type
    psn    = ProcessSerialNumber(0, kCurrentProcess)
    ApplicationServices.TransformProcessType(psn, kProcessTransformToUIElementAppication)
    screen = NSScreen.mainScreen()
    myWindow = FullScreenWindow.alloc().initWithContentRect_styleMask_backing_defer_(screen.frame(), NSBorderlessWindowMask, NSBackingStoreBuffered, True)
    myView = LockView.alloc().initWithFrame_(screen.frame())
    myWindow.setContentView_(myView)
    myWindow.setLevel_(kCGDesktopWindowLevel)
    myWindow.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorStationary | NSWindowCollectionBehaviorIgnoresCycle)
    myWindow.setBackgroundColor_(NSColor.blackColor())
    myWindow.makeKeyAndOrderFront_(myWindow)
    myWindow.display()
    controller = MainController.alloc().init()
    controller.run()

def main():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(script_directory, backdrop_filename)
    # This is an example of how to use show_backdrop
    # show_backdrop will actually be spun up in a new forked process via multiprocessing, but we will want to tell it to terminate at some point
    # so we create a multiprocessing.Queue and pass that as the only arg to the new process
    # This Queue is now a shared communication method. The controller loop of the new process checks every 1 second
    # to see if anything is in the queue - if it is, it terminates.
    # Build the queue
    comm_queue = multiprocessing.Queue()
    # Configure the new process
    background_process = multiprocessing.Process(target=show_backdrop, args=(comm_queue,image_path))
    # Start the process
    background_process.start()
    # [ Do whatever else python / logic / whatever you want to do ]
    # Filler example!
    print "Hi, look, more code is running! (in the original process - the background is in a new one)"
    ignored = raw_input("Type something: ")
    print "Woo, we did more stuff"
    ignored = raw_input("Press enter when you're ready to kill the background")
    # Put anything on the queue
    comm_queue.put(0)
    print "The backdrop should have disappeared in a second, we'll pause in a sec here though to show code is still running"
    for x in range(10):
        time.sleep(0.15)
        print "%s of 10" % (x+1)
    ignored = raw_input("Press enter when you're proven it to yourself")
    print "Demo complete"

if __name__ == '__main__':
    main()
