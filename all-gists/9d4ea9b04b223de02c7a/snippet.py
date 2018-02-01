import re
import idaapi
import sark
import abc


class IDATracker(idaapi.UI_Hooks):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(IDATracker, self).__init__()

    def updating_actions(self, ctx=idaapi.action_update_ctx_t()):
        if ctx.form_type == idaapi.BWN_DISASM:
            self.on_ea(ctx.cur_ea, ctx)

    @abc.abstractmethod
    def on_ea(self, ea, ctx):
        return NotImplemented


def get_base_name(function):
    true_name = function.demangled
    match = re.search(r'([\w]+)\(', true_name)
    if not match:
        return
    return match.group(1)

def hint_function(ea):
    try:
        function = sark.Function(ea)
    except sark.exceptions.SarkNoFunction:
        return
    base_name = get_base_name(function)
    function.lines.next().comments.posterior = 'Base name: {}'.format(base_name)


class FunctionHinter(IDATracker):
    def __init__(self):
        super(FunctionHinter, self).__init__()

        self.current_ea = None

    def on_ea(self, ea, ctx):
        if sark.is_same_function(self.current_ea, ea):
            return

        hint_function(ea)
        self.current_ea = ea


hinter = FunctionHinter()
hinter.hook()
