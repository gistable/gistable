import lldb
import commands
import optparse
import shlex


def __lldb_init_module (debugger, dict):
	debugger.HandleCommand('command script add -f windowDescription.window_description_command window_description')
	print 'The "window_description" command has been installed'
	
def window_description_command(debbuger, command, result, dict):
	debbuger.HandleCommand('expr UIApplication *$uiapp = [UIApplication sharedApplication]')
	debbuger.HandleCommand('expr UIApplication *$kw = [$uiapp keyWindow]')
	debbuger.HandleCommand('po [$kw recursiveDescription]')