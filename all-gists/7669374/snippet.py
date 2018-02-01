# -*- coding: utf-8 -*-

import re
import lldb


def lsview(debugger, command, result, internal_dict):
    root_view = _get_root_view()
    view_hierarchy = get_view_hierarchy(root_view)
    print_view_hierarchy(view_hierarchy)


def print_view_hierarchy(view_hierarchy, indent=0):
    view = view_hierarchy['view']
    print '%s%s' % (' ' * indent, UIView.description(view))
    for subview in view_hierarchy['subviews']:
        print_view_hierarchy(subview, indent=indent+4)


def get_view_hierarchy(root_view):
    view_hierarchy = {
        'view': root_view,
        'subviews': [],
    }
    subviews = UIView.subviews(root_view)
    for i in range(0, NSArray.count(subviews)):
        view = NSArray.object_at_index(subviews, i, "UIView*")
        view_hierarchy['subviews'].append(get_view_hierarchy(view))
    return view_hierarchy


def _get_root_view():
    return _eval("(UIView *)[[[UIWindow keyWindow] rootViewController] view]").GetValue()


def _eval(expression):
    thread = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread()
    frame = thread.frames[0]
    return frame.EvaluateExpression(expression)


def exe(debugger, command, result, internal_dict):
    _eval("(void)%s" % command)
    _eval("(void)[[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.0001]]")


class UIView():
    description_pattern = re.compile('"(.*)"')
    @classmethod
    def subviews(cls, view):
        return _eval("(NSArray *)[%s subviews]" % view).GetValue()
    @classmethod
    def description(cls, view):
        string_obj = _eval("(NSString *)[%s description]" % view).GetValue()
        string = NSString.utf8string(string_obj)
        return cls.description_pattern.sub(r'\1', string)


class NSArray():
    @classmethod
    def count(cls, array):
        return int(_eval("(int)[%s count]" % array).GetValue())

    @classmethod
    def object_at_index(cls, array, i, type):
        return _eval("(%s)[%s objectAtIndex:%d]" % (type, array, i)).GetValue()


class NSString():
    @classmethod
    def utf8string(cls, string):
        return _eval("(const char *)[%s UTF8String]" % string).GetSummary()


def __lldb_init_module (debugger, dict):
    debugger.HandleCommand('command script add -f lsview.lsview lsview')
    debugger.HandleCommand('command script add -f lsview.exe exe')
