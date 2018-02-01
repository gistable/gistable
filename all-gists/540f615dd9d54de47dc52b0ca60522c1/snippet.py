import idc
import idaapi
import idautils


def rename_sub_functions(fva, prefix):
    sub_funcs = set([])
    for f in idautils.Functions():
        for xref in idautils.XrefsTo(f):
            subf = idaapi.get_func(xref.frm)
            if not subf:
                continue

            if subf.startEA == fva:
                sub_funcs.add(f)
                break

    for sub_func in sub_funcs:
        current_name = idc.GetFunctionName(sub_func)
        if current_name.startswith(prefix):
            continue
        new_name = prefix + current_name
        idc.MakeName(sub_func, new_name)

if __name__ == '__main__':
    rename_sub_functions(idc.ScreenEA(), "test_")