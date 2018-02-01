import sys, os, os.path, tempfile, plistlib, shutil, marshal, subprocess, pickle, textwrap

class TempApp(object):
    _skeleton_app = textwrap.dedent("""
                      import sys, marshal, types, pickle
                      main_func_marshal = %s
                      args_pickle       = %s
                      code = marshal.loads(main_func_marshal)
                      main_func = types.FunctionType(code, globals(), "main_func")
                      args = dict(pickle.loads(args_pickle))
                      returncode, result = main_func(args)
                      print pickle.dumps(result)
                      sys.exit(returncode)
                      """)
    def __init__(self, infoPlist_dict, app_path=None, bundle_name='TempApp', cleanup=True, app_icon=None):
        # infoPlist_dict: A dict containing key values that should be set/overridden
        #                 vs. the normal Python.app keys.
        #       app_path: The path to where your app should go. Example: '/usr/local/myOrgStuff'
        #                 This directory needs to pre-exist. If app_path is left at None,
        #                 a temporary directory will be created and used and the value of
        #                 cleanup will be forced to True
        #    bundle_name: The name of your .app. This tends to be what shows in the Dock.
        #                 Spaces in the name are ok, but keep it short.
        #        cleanup: If app_path is provided, cleanup set to False will leave the .app
        #                 bundle behind rather than removing it on object destruction.
        #       app_icon: Set to the path of a .icns file if you wish to have a custom app icon
        #
        # Setup our defaults
        super(type(self), self).__init__()
        self.path           = None
        self.cleanup_parent = False
        self.cleanup        = cleanup
        self.returncode     = 0
        # First we look up which python we're running with so we know which Python.app to clone
        # ... We'll just cheat and use the path of 'os' which we already imported.
        base_python = os.__file__.split(os.path.join('lib', 'python2'),1)[0]
        python_app  = os.path.join(base_python, 'Resources', 'Python.app')
        app_name = '%s.app' % (os.path.basename(bundle_name))
        # Now we setup where we want the new Python.app clone to go
        if app_path is None:
            # Dynamically generate a path and force the value of cleanup
            self.cleanup        = True
            # Also need to cleanup the temp directory we made
            self.cleanup_parent = True
            app_path  = tempfile.mkdtemp()
        else:
            # Verify the parent path exists
            # Trim trailing slashes
            tmp_path = os.path.normpath(app_path)
            if not os.path.exists(tmp_path):
                raise Exception('app_path supplied "%s" does not exist' % app_path)
            elif not os.path.isdir(tmp_path):
                raise Exception('app_path supplied "%s" does not appear to be a directory' % app_path)
            app_path = tmp_path
        if app_icon is not None:
            if not os.path.exists(app_icon):
                raise Exception('app_icon supplied "%s" does not exist' % app_icon)
            elif not os.path.isfile(app_icon):
                raise Exception('app_icon supplied "%s" does not appear to be a file' % app_icon)
        self.path = os.path.join(app_path, app_name)
        # Make the bundle directory
        os.mkdir(self.path)
        os.makedirs(os.path.join(self.path, 'Contents', 'MacOS'))
        # Set up symlink contents
        os.symlink(os.path.join(python_app, 'Contents', 'MacOS', 'Python'), os.path.join(self.path, 'Contents', 'MacOS', 'Python'))
        os.symlink(os.path.join(python_app, 'Contents', 'PkgInfo'), os.path.join(self.path, 'Contents', 'PkgInfo'))
        if app_icon is not None:
            # We create a custom Resources folder and copy the .icns file to the default 'PythonInterpreter.icns' inside
            os.makedirs(os.path.join(self.path, 'Contents', 'Resources'))
            shutil.copyfile(app_icon, os.path.join(self.path, 'Contents', 'Resources', 'PythonInterpreter.icns'))
        else:
            # No app_icon provided, just use the default resources
            os.symlink(os.path.join(python_app, 'Contents', 'Resources'), os.path.join(self.path, 'Contents', 'Resources'))
        os.symlink(os.path.join(python_app, 'Contents', 'version.plist'), os.path.join(self.path, 'Contents', 'version.plist'))
        # Grab the contents of the existing Info.plist ... yes, using plistlib - this Info.plist is so far only XML ...
        original_infoPlist = plistlib.readPlist(os.path.join(python_app, 'Contents', 'Info.plist'))
        # Make our changes from infoPlist_dict
        original_infoPlist.update(infoPlist_dict)
        # Write the contents back to the new location
        plistlib.writePlist(original_infoPlist, os.path.join(self.path, 'Contents', 'Info.plist'))
    def cleanup_app(self):
        # Kill the process if it's still running
        if self.cleanup:
            # Delete the .app bundle, best effort
            try:
                shutil.rmtree(self.path, True)
            except:
                pass
        if self.cleanup_parent:
            # This was an auto-generated directory, remove it as well
            try:
                shutil.rmtree(os.path.dirname(self.path), True)
            except:
                pass
    def __del__(self):
        self.cleanup_app()
    def run(self, func, **kwargs):
        # Spawn an instance of this app bundle, passing func as the core of the new process.
        # Keyword arguments are passed as a dictionary to the new process's core function.
        # marshal up the function
        main_func_marshal = marshal.dumps(func.func_code).__repr__()
        # pickle up the args
        args_pickle = pickle.dumps(kwargs.items()).__repr__()
        # build the core code
        new_app = self._skeleton_app % (main_func_marshal, args_pickle)
        # Spawn the new process
        proc = subprocess.Popen([os.path.join(self.path, 'Contents', 'MacOS', 'Python'), '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Give it the code
        proc.stdin.write(new_app)
        # Let it run to completion, record output
        sout, serr = proc.communicate()
        # Record returncode
        self.returncode = proc.returncode
        result = None
        try:
            result = pickle.loads(sout)
        except:
            pass
        return result

def example_main_function(args_dict):
    # Do all your imports, classes, functions, etc. internal to your this application core function
    # Everything needs to be defined here
    # The return value from it should be a tuple: (process returncode [0 = success], pickle-able return result data)
    from AppKit import NSApp, NSApplication, NSAlert, NSInformationalAlertStyle, NSTimer
    class OKAlert(object):
        def __init__(self, message, buttons=None):
            super(type(self), self).__init__()
            self.alert = None
            self.message = message
            self.buttons = buttons
            self.result_code = None
        def runAndStop_(self, timer):
            self.alert = NSAlert.alloc().init()
            self.alert.setAlertStyle_(NSInformationalAlertStyle)
            self.alert.setMessageText_(self.message)
            if self.buttons is None:
                self.alert.addButtonWithTitle_('OK')
            else:
                for x in self.buttons:
                    self.alert.addButtonWithTitle_(x)
            NSApp.activateIgnoringOtherApps_(True)
            self.result_code = self.alert.runModal()
            NSApp.stop_(None)
        def run(self):
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.1, self, 'runAndStop:', '', False)
            NSApplication.sharedApplication()
            NSApp.run()
    # Create our dialog
    dialog = OKAlert(args_dict.get('message'), args_dict.get('buttons'))
    # Run our dialog
    dialog.run()
    # (returncode [0 = success], results)
    return (0, dialog.result_code)

# How to use it
infoPlist_overrides = {'CFBundleName': 'Menu Name'}
myApp  = TempApp(infoPlist_overrides, bundle_name='Dock Name', app_icon='/Users/mike/Desktop/tinker.icns')
result = myApp.run(example_main_function, message='The message was Hello!', buttons=['1st Button'])
