import idaapi
import idc


class HexJumpHandler(idaapi.action_handler_t):
    def activate(self, ctx):
        selection = idaapi.read_selection()
        valid_selection = selection[0]
        if (valid_selection):
            addr = idc.DbgDword(selection[1])
            idaapi.jumpto(addr)
        else:
            idaapi.msg("Invalid selection!\n")

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


class HexJumpHooks(idaapi.UI_Hooks):
    def finish_populating_tform_popup(self, form, popup):
        if idaapi.get_tform_type(form) == idaapi.BWN_DUMP:
            desc = idaapi.action_desc_t(None, 'Follow in hex dump', HexJumpHandler())
            idaapi.attach_dynamic_action_to_popup(form, popup, desc, None)


class HexJump(idaapi.plugin_t):
    flags = idaapi.PLUGIN_KEEP
    comment = "Easily follow DWORD addresses within hex dump"
    help = "Highlight DWORD address within hex dump and right-click 'Follow in hex dump'"
    wanted_name = "HexJump"
    wanted_hotkey = ""

    def init(self):
        global hooks
        hooks = HexJumpHooks()
        re = hooks.hook()
        return idaapi.PLUGIN_OK

    def run(self, arg):
        pass

    def term(self):
        pass


def PLUGIN_ENTRY():
    return HexJump()
