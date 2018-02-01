'''
Break on Objective-C 's method using its address'
'''
import shlex
import lldb
import re
def breakonmethod(debugger, command, exe_ctx,result, internal_dict):
    args=shlex.split(command)
    Class=args[0]
    Method=args[1]
    ClassMethod = lldb.SBCommandReturnObject()
    CMCommand='expr -- (IMP)method_getImplementation((Method)class_getClassMethod((Class)objc_getClass("{0}"),@selector({1})));'.format(Class,Method)
    IMCommand='expr -- (IMP)method_getImplementation((Method)class_getInstanceMethod((Class)objc_getClass("{0}"),@selector({1})));'.format(Class,Method)
    debugger.GetCommandInterpreter().HandleCommand(CMCommand, ClassMethod)
    InstanceMethod =lldb.SBCommandReturnObject()
    debugger.GetCommandInterpreter().HandleCommand(IMCommand,InstanceMethod)
    CMObj=ClassMethod.GetOutput()
    IMObj=InstanceMethod.GetOutput()
    CMObj=re.search(r'0x([a-zA-Z0-9]|x)*', CMObj).group(0)
    IMObj=re.search(r'0x([a-zA-Z0-9]|x)*', IMObj).group(0)
    CMObj=int(CMObj, 16)
    IMObj=int(IMObj, 16)
    ADDR=max(CMObj,IMObj)
    debugger.HandleCommand("breakpoint set -a %i"%ADDR)
def __lldb_init_module (debugger, dict):
#Avoid Name Collision
  debugger.HandleCommand('command script add -f BreakMessage.breakonmethod bom')
