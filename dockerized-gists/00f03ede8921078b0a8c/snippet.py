def get_obj_attr(root, str_path, default_val="", debug=False):
    attr_path = str_path.split(".")
    base_obj = root
    for attr in attr_path:
        if hasattr(base_obj, attr):
            base_obj = base_obj.__dict__[attr]
        else:
            if debug:
                print "No attribute: %s" % attr
            base_obj = default_val
            break
    if base_obj != default_val:
        base_obj = unicode(base_obj)
    return base_obj
