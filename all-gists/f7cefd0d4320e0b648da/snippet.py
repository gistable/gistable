class ProgressDialog(object):
    def __init__(self, message, title, use_bar=True):
        super(self.__class__, self).__init__()
        self.message = message
        self.title   = title
        self.use_bar = use_bar
        self.queue   = None
        self.process = None
    def display(self):
        # [ begin black magic ]
        def _run_progress(comm_queue, message_txt, title_txt, use_bar):
            from AppKit import NSBundle, NSApplication, NSWindow, NSApp, NSScreen, NSMakeRect, NSMakePoint, NSProgressIndicator, NSWindow, \
                               NSTitledWindowMask, NSBackingStoreBuffered, NSProgressIndicatorPreferredAquaThickness, NSTextField, \
                               NSStatusWindowLevel, NSProgressIndicatorBarStyle, NSProgressIndicatorSpinningStyle, NSObject, \
                               NSApplicationDefined, NSEvent, NSTimer, NSSmallControlSize
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
                    NSApp.activateIgnoringOtherApps_(True)
                    NSApp.run()
            # Evil hack to make this process not show in the Dock
            bundle = NSBundle.mainBundle()
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            info['LSUIElement'] = '1'
            # Create our NSApplication instance
            app = NSApplication.sharedApplication()
            # Create a window, size doesn't matter now, we're going to resize it in the end
            window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(0, 0, 500, 500), NSTitledWindowMask, NSBackingStoreBuffered, True)
            # Build the window from the bottom up
            # Create the progress indicator, placement doesn't matter, will be set later
            progress = NSProgressIndicator.alloc().init()
            if use_bar:
                progress.setStyle_(NSProgressIndicatorBarStyle)
            else:
                progress.setStyle_(NSProgressIndicatorSpinningStyle)
            progress.setUsesThreadedAnimation_(True)
            progress.setIndeterminate_(True)
            progress.startAnimation_(None)
            # Create the text, which will define the width of everything else - size doesn't matter at first...
            message = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 50, 20, 20))
            message.setStringValue_(message_txt)
            message.setBezeled_(False)
            message.setDrawsBackground_(False)
            message.setEditable_(False)
            message.setSelectable_(False)
            # Resize the field to fit the text
            message.sizeToFit()
            window.contentView().addSubview_(message)
            # Now we can calculate the width
            # Fix the window geometry
            # A default NSAlert is 420x150, let's aim for something with similar geometry!
            frame = NSMakeRect(0, 0, max(420, message.frame().size.width + 40), 110)
            screen = NSScreen.mainScreen()
            screenFrame = screen.frame()
            # Fix the progressbar geometry
            if use_bar:
                # Set the bar to stretch the width of the dialog
                progress.setFrame_(NSMakeRect(20, 20, frame.size.width - 40, NSProgressIndicatorPreferredAquaThickness))
            else:
                # Center the spinning wheel at the bottom
                progress.setControlSize_(NSSmallControlSize)
                progress.setFrame_(NSMakeRect((frame.size.width/2) - 8, 20, 16, 16))
            window.contentView().addSubview_(progress)
            # Pleasant centering, 2/3rds of the way up, in the middle
            highCenterPoint = NSMakePoint((screenFrame.size.width / 2) - (frame.size.width / 2), 1.3*(screenFrame.size.height / 2) - (frame.size.height / 2))
            window.setFrame_display_animate_(frame, True, False)
            window.setFrameOrigin_(highCenterPoint)
            window.makeKeyAndOrderFront_(None)
            window.setLevel_(NSStatusWindowLevel)
            window.setTitle_(title_txt)
            window.display()
            controller = MainController.alloc().init()
            controller.run()
        # [ more black magic ]
        import multiprocessing
        self.queue   = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=_run_progress, args=(self.queue, self.message, self.title, self.use_bar))
        self.process.start()
    def close(self):
        # [ darkest black magic ]
        self.queue.put(0)
        self.process.join()

# Example usage of the ProgressDialog class

import time

def demo():
    # Bar
    my_bar_dialog = ProgressDialog("Please wait while we make some (fake) changes ...", "Please Wait (title!)", use_bar=True)
    my_bar_dialog.display()
    # ... continue to do code here ...
    # (we'll just sleep 5 seconds as a demo)
    print "code"
    time.sleep(2)
    print "is"
    time.sleep(2)
    print "still"
    time.sleep(2)
    print "running\n"
    time.sleep(2)
    my_bar_dialog.close()
    # Spinner
    my_spin_dialog = ProgressDialog("Oh no, what could be wrong ?? This message is ever so much wider, does this thing adjust??", "Please Panic", use_bar=False)
    my_spin_dialog.display()
    # ... continue to do code here ...
    # (we'll just sleep 5 seconds as a demo)
    print "keep"
    time.sleep(2)
    print "calm"
    time.sleep(2)
    print "carry"
    time.sleep(2)
    print "on"
    time.sleep(2)
    my_spin_dialog.close()

demo()
