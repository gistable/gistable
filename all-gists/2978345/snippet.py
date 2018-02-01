MBA-FBA:bin francois$ ./virt-manager
RuntimeWarning: tp_compare didn't return -1 or -2 for exception
RuntimeWarning: tp_compare didn't return -1 or -2 for exception
Traceback (most recent call last):
  File "/Users/francois/bin/mybuild/share/virt-manager/virt-manager.py", line 393, in <module>
    _show_startup_error(str(run_e), "".join(traceback.format_exc()))
  File "/Users/francois/bin/mybuild/share/virt-manager/virt-manager.py", line 63, in _show_startup_error
    from virtManager.error import vmmErrorDialog
  File "/Users/francois/bin/mybuild/share/virt-manager/virtManager/error.py", line 173, in <module>
    class _errorDialog (gtk.MessageDialog):
AttributeError: 'module' object has no attribute 'MessageDialog'
