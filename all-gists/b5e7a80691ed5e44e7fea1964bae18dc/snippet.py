'''
example of:
  - using ctypes with the IDA SDK
  - providing custom UI hints with dynamic data from Python

in this silly example, we display UI hints with the current timestamp.
a more useful plugin might inspect the hovered line, and display some documentation.

Author: Willi Ballenthin <william.ballenthin@fireeye.com>
Licence: Apache 2.0
'''
import sys
import ctypes

import idc
import idaapi
import idautils


def get_ida_ctypes():
    '''
    get the ida sdk dll.
    
    Args: None

    Returns:
      ctypes.CDLL: the IDA SDK DLL

    via: http://www.hexblog.com/?p=695
    '''
    idaname = 'ida64' if __EA64__ else 'ida'
    if sys.platform == 'win32':
        return ctypes.windll[idaname + '.wll']
    elif sys.platform == 'linux2':
        return ctypes.cdll['lib' + idaname + '.so']
    elif sys.platform == 'darwin':
        return ctypes.cdll['lib' + idaname + '.dylib']
    else:
        raise RuntimeError('unknown platform: ' + sys.platform)


c_long_p = ctypes.POINTER(ctypes.c_long)
c_int_p = ctypes.POINTER(ctypes.c_int)
c_char_pp = ctypes.POINTER(ctypes.c_char_p)
    

# ctypes declaration for the `hook_type_t` type.
#
# the idaapi calling convention is stdcall, so we use WINFUNCTYPE;
#  it is *not* cdecl (ctypes.CFUNCTYPE).
#
# relevant idasdk documentation: 
#
#    typedef int idaapi hook_cb_t(
#      void *user_data,
#      int notification_code,
#      va_list va);
HookCb = ctypes.WINFUNCTYPE(
    # return type
    ctypes.c_int,      # int idaapi

    # argument types
    ctypes.c_void_p,   # void       *user_data
    ctypes.c_int,      # int         notification_code
    ctypes.c_void_p,   # va_list     va 
)


class HOOK_TYPES:
    '''
    types of events that be hooked to with hook_to_notification_point().
    this corresponds to `hook_type_t`.
    '''
    # Hook to the processor module.
    HT_IDP = 0

    # Hook to the user interface.
    HT_UI = 1

    # Hook to the debugger.
    HT_DBG = 2

    # Hook to the database events.
    HT_IDB = 3

    # Internal debugger events.
    HT_DEV = 4

    # Custom/IDA views notifications.
    HT_VIEW = 5

    # Output window notifications.
    HT_OUTPUT = 6

    HT_LAST = 7


def do_hook_to_notification_point(dll, hook_type, cb, user_data):
    '''
    register a callback for a class of events in IDA.
    
    Args:
      dll (ctypes.CDLL): the IDA SDK DLL
      hook_type (int): hook type from HOOK_TYPES enum
      cb (HookCb): the callback to register
      user_data (ctypes.c_void_p): context provided to callback when invoked
    
    Returns: None

    relevant idasdk documentation: 

        idaman bool ida_export 	
        hook_to_notification_point (
            hook_type_t hook_type,
            hook_cb_t *cb,
            void *user_data)
   '''
    
    hook_to_notification_point = dll.hook_to_notification_point
    hook_to_notification_point.argtypes = [
        ctypes.c_int,      # hook_type_t hook_type
        HookCb,            # hook_cb_t  *cb
        ctypes.c_void_p,   # void       *user_data
    ]

    hook_to_notification_point(hook_type, cb, user_data)


def do_unhook_from_notification_point(dll, hook_type, cb, user_data):
    '''
    unregister a callback.
    
    Args:
      dll (ctypes.CDLL): the IDA SDK DLL
      hook_type (int): hook type from HOOK_TYPES enum
      cb (HookCb): the callback to register
      user_data (ctypes.c_void_p): context provided to callback when invoked
    
    Returns: None

    relevant idasdk documentation: 

        idaman bool ida_export 	
        unhook_from_notification_point (
            hook_type_t hook_type,
            hook_cb_t *cb,
            void *user_data = NULL)
   '''
    
    unhook_from_notification_point = dll.unhook_from_notification_point
    unhook_from_notification_point.argtypes = [
        ctypes.c_int,      # hook_type_t hook_type
        HookCb,            # hook_cb_t  *cb
        ctypes.c_void_p,   # void       *user_data
    ]

    unhook_from_notification_point(hook_type, cb, user_data)


class UI_NOTIFICATIONS:

    # get single line hint for the given address.
    # this is *not* used for the disasm listing hover tooltips.
    # this is used for nav bar hover tooltips.
    # 
    # relevant idasdk documentation: 
    #
    #     cb: ui wants to display a simple hint for an address.
    #     Use this event to generate a custom hint
    #     See also more generic ::ui_get_item_hint
    #     \param ea       (::ea_t)
    #     \param buf      (char *)
    #     \param bufsize  (size_t)
    #     \return true if generated a hint
    UI_GET_EA_HINT = 79

    # i'm not sure where this is called.
    #
    # relevant idasdk documentation: 
    #
    #     cb: ui wants to display multiline hint for an item.
    #     See also more generic ::ui_get_custom_viewer_hint
    #     \param ea (ea_t, or item id like a structure or enum member)
    #     \param max_lines             (int) maximal number of lines
    #     \param[out] important_lines  (int *) number of important lines. if zero, output is ignored
    #     \param[out] hint             (::qstring *) the output string
    #     \return true if generated a hint
    UI_GET_ITEM_HINT = 80

    # get multiple line hint for the given address
    # this is invoked for at least the following views:
    #   - disasm
    #   - enums
    #   - structures
    # 
    # relevant idasdk documentation: 
    #
    #     cb: ui wants to display a hint for a viewer (idaview or custom).
    #     \param viewer (TCustomControl*) viewer
    #     \param place                 (::place_t *) current position in the viewer
    #     \param[out] important_lines  (int *) number of important lines.
    #                                         if zero, the result is ignored
    #     \param[out] hint             (::qstring *) the output string
    #     \return true if generated a hint
    UI_GET_CUSTOM_VIEWER_HINT = 91


class DynHintsPlugin(idaapi.plugin_t):
    flags = idaapi.PLUGIN_KEEP
    comment = "Display dynamically-generated hints."

    help = "Display dynamically-generated hints."
    wanted_name = "DynHints"
    wanted_hotkey = "Ctrl-]"

    def init(self):
        import datetime
        self.dll = get_ida_ctypes()

        # can't use a bound method as a callback (since `self` doesn't get provided)
        #  so we'll create a closure that has access to `self`.
        # 
        # via: http://stackoverflow.com/a/7261524/87207
        def cb(user_data, notification_code, va_list):
            '''
            example hook_cb_t function that handles custom viewer hints.

            Args:
              user_data (ctypes.c_void_p): context supplied to callback registration
              notification_code (int): one of the UI_NOTIFICATIONS enum values
              va_list (ctypes.c_void_p): varargs that must be manually parsed

            Returns:
              int: see notifiication code documentation for interpretation

            Notes:
              - This is a closure that expects to have 
            '''

            # this function is called *a lot*, so don't do any heavy lifting
            #  until you know its the event you want.

            # ctypes doesn't support varargs in callback functions.
            # so, we need to parse the remaining arguments ourselves.
            #
            # on windows, varargs are sequential stack locations.
            # so, lets access the members like an array of ints/pointers.
            #
            # WARNING: the following section that manually parses varargs is
            #  probably architecture and platfrom dependent!
            va_list = ctypes.cast(va_list, c_long_p)

            if notification_code == UI_NOTIFICATIONS.UI_GET_EA_HINT:
                # ea is just a number: 
                #
                #     typedef uint32 	ea_t
                #
                # via: https://www.hex-rays.com/products/ida/support/sdkdoc/pro_8h.html#a7b0aeaed04e477c02cf8ea3452002d1a
                ea = va_list[0]
                buf = ctypes.cast(va_list[1], ctypes.c_char_p)
                bufsize = va_list[2]

                print('ui_get_ea_hint:')
                print('>.. notification code: %s' % (notification_code))
                print('>.. ea: %s' % (hex(ea)))
                print('>.. buf: %s' % (buf))
                print('>.. bufsize: %s' % (hex(bufsize)))

                the_hint = datetime.datetime.now().isoformat(' ')

                self.dll.qstrncpy(buf, ctypes.c_char_p(the_hint), bufsize)
                print('<.. buf: %s' % (buf))

                return 1

            elif notification_code == UI_NOTIFICATIONS.UI_GET_CUSTOM_VIEWER_HINT:
                viewer = ctypes.cast(va_list[0], c_long_p)
                place = ctypes.cast(va_list[1], c_long_p)
                important_lines = ctypes.cast(va_list[2], c_long_p)
                hint = ctypes.cast(va_list[3], c_char_pp)

                if not place:
                    print('ui_get_custom_viewer_hint: invalid place')
                    return 0

                print('ui_get_custom_viewer_hint:')
                print('>.. notification code: %s' % (notification_code))
                print('>.. important lines: %s %s' % (important_lines, important_lines.contents))
                print('>.. hint: %s %s' % (hint, hint.contents))

                # so, we'd like to fetch the EA of the current view.
                # ideally, we'd do:
                #
                #     ea = place.toea()
                #
                # but `place` is a raw c++ object pointer, and ctypes isn't that smart.
                # next best would be to do something like:
                #
                #     place = self.dll.get_custom_viewer_place(viewer);
                #
                # however, this doesn't work because `get_custom_viewer_place` is not an exported routine.
                # it seems to be part of the IDA SDK static lib to which plugins link.
                #
                # next best would be to use `idaapi.get_custom_viewer_place`:
                #
                #     place = idaapi.get_custom_viewer_place(viewer);
                #
                # but, this doesn't work because we're mixing a ctypes pointer with a swig function.
                # so, we'll fall back to querying the current viewer, and fetching the place from there.

                # let's only display for disassembly listings
                #
                # i only know how to test the view/form type using the `get_tform_type` function.
                # therefore, we'll first query the current tform, and subsequently the current custom_viewer.
                tform = idaapi.get_current_tform()
                if idaapi.get_tform_type(tform) != idaapi.BWN_DISASM:
                    return 0

                viewer = idaapi.get_current_viewer()

                # `place` is a tuple (though techincally, a list), with elements:
                #  - place_t proxy
                #  - x position in characters
                #  - y position in characters from top of screen/form (-1 in graph view)
                place, x, y = idaapi.get_custom_viewer_place(viewer, True)

                the_hint = '0x%08X: %s' % (place.toea(), datetime.datetime.now().isoformat(' '))

                important_lines[0] = ctypes.c_long(1)
                # we don't have access to the qstring c++ class methods,
                #  so we'll use a dummy routine to correctly set our qstring contents.
                # `replace_tabs` assigns from a char * to a qstring *.
                #
                # relevant idasdk documentation: 
                #
                #    idaman THREAD_SAFE bool ida_export
                #    replace_tabs (
                #        qstring *out,
                #        const char *str,
                #        int tabsize)
                self.dll.replace_tabs(hint, ctypes.c_char_p(the_hint), 4)

                print('<.. important lines: %s %s' % (important_lines, important_lines.contents))
                print('<.. hint: %s %s' % (hint, hint.contents))

                return 1

            return 0


        # need to keep a ref around, or the function gets garbage collected
        self.cb = HookCb(cb)

        # need to keep a ref around, or the param gets garbage collected
        self.ctx = ctypes.c_long(69)

        return idaapi.PLUGIN_OK

    def run(self, arg):
        print('hints: run')
        do_hook_to_notification_point(self.dll, HOOK_TYPES.HT_UI, self.cb, ctypes.byref(self.ctx))

    def term(self):
        print('hints: term')
        do_unhook_from_notification_point(self.dll, HOOK_TYPES.HT_UI, self.cb, ctypes.byref(self.ctx))


def PLUGIN_ENTRY():
    return DynHintsPlugin()
