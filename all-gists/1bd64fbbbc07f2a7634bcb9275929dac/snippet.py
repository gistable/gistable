import idaapi
import idautils

def iter_all_funcs():
    for func_ea in idautils.Functions(idaapi.cvar.inf.minEA, idaapi.cvar.inf.maxEA):
        yield idaapi.get_func(func_ea)

def iter_multichunk_funcs():
    for func_t in iter_all_funcs():
        if func_t.tailqty > 0:
            yield func_t

def delete_multichunk_funcs():
    for func_t in iter_multichunk_funcs():
        idaapi.del_func(func_t.startEA)