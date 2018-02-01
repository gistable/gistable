    if rep.failed:
        if hasattr(rep.longrepr, "sections"):
            local_vars = call.excinfo.traceback[-1].locals
            longest_name = max([len(str(item)) for item in local_vars.keys()])
            local_list = []
            for item, value in local_vars.items():
                if str(value) not in repr(value):
                    single_local_str = "{:%s} = " % longest_name
                    single_local_str = single_local_str.format(item)
                    single_local_str += "  {}".format(str(value).strip())
                    local_list.append(single_local_str)
            local_str = "\n".join(local_list)
            rep.longrepr.sections.append(("str(Locals)", local_str, '-'))