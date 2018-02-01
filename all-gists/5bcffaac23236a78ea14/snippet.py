#
# Show a hint when the user has his mouse on an instruction
#
import idaapi
import idautils

class Hooks(idaapi.UI_Hooks):
    def get_custom_viewer_hint(self, view, place):
        insn = idautils.DecodeInstruction(place.toea())
        if insn:
            hint = "Instruction is a: %s" % insn.get_canon_mnem()
            return (hint, 1)

myHook = Hooks()
myHook.hook()