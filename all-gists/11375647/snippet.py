import lldb
import commands


def __lldb_init_module (debugger, dict):
	debugger.HandleCommand('command script add -f LBRShortcut.window_description_command window_description')
	debugger.HandleCommand('command script add -f LBRShortcut.json_data_command json_data')
	debugger.HandleCommand('command script add -f LBRShortcut.fire_fault_command fire_fault')
	
def window_description_command(debbuger, command, result, dict):
	debbuger.HandleCommand('expr UIApplication *$uiapp = [UIApplication sharedApplication]')
	debbuger.HandleCommand('expr UIApplication *$kw = [$uiapp keyWindow]')
	debbuger.HandleCommand('po [$kw recursiveDescription]')

		
def fire_fault_command(debugger, command, result, dict):
	# command regex fire_fault 's/(.+)/po [%1 willAccessValueForKey:nil]/'
    if len(command) == 0:
        print "You need to specify the name of a variable"
        return
        
    variable_arg = command
    debugger.HandleCommand('expr [' + variable_arg +' willAccessValueForKey:nil]')

	
def json_data_command(debugger, command, result, dict):
	if len(command) == 0:
		print "You need to specify the name of a variable"
		return

	variable_arg = command
	debugger.HandleCommand('po [NSJSONSerialization JSONObjectWithData:' + variable_arg +' options:0 error:nil]')