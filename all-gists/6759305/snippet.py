import lldb
import re
import shlex

# This script allows Xcode to selectively ignore Obj-C exceptions
# based on any selector on the NSException instance

def getRegister(target):
    if target.triple.startswith('x86_64'):
        return "rdi"
    elif target.triple.startswith('i386'):
        return "eax"
    elif target.triple.startswith('arm64'):
        return "x0"
    else:
        return "r0"

def callMethodOnException(frame, register, method):
    return frame.EvaluateExpression("(NSString *)[(NSException *)${0} {1}]".format(register, method)).GetObjectDescription()

def filterException(debugger, user_input, result, unused):
    target = debugger.GetSelectedTarget()
    frame = target.GetProcess().GetSelectedThread().GetFrameAtIndex(0)

    if frame.symbol.name != 'objc_exception_throw':
        # We can't handle anything except objc_exception_throw
        return None

    filters = shlex.split(user_input)

    register = getRegister(target)


    for filter in filters:
        method, regexp_str = filter.split(":", 1)
        value = callMethodOnException(frame, register, method)

        if value is None:
            output = "Unable to grab exception from register {0} with method {1}; skipping...".format(register, method)
            result.PutCString(output)
            result.flush()
            continue

        regexp = re.compile(regexp_str)

        if regexp.match(value):
            output = "Skipping exception because exception's {0} ({1}) matches {2}".format(method, value, regexp_str)
            result.PutCString(output)
            result.flush()

            # If we tell the debugger to continue before this script finishes,
            # Xcode gets into a weird state where it won't refuse to quit LLDB,
            # so we set async so the script terminates and hands control back to Xcode
            debugger.SetAsync(True)
            debugger.HandleCommand("continue")
            return None

    return None

def __lldb_init_module(debugger, unused):
    debugger.HandleCommand('command script add --function ignore_specified_objc_exceptions.filterException ignore_specified_objc_exceptions')
