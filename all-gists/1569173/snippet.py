import os

def del_empty_dirs(s_dir,f):
    b_empty = True

    for s_target in os.listdir(s_dir):
        s_path = os.path.join(s_dir, s_target)
        if os.path.isdir(s_path):
            if not del_empty_dirs(s_path):
                b_empty = False
        else:
            b_empty = False

    if b_empty:
        print('del: %s' % s_dir)
        os.rmdir(s_dir)

    return b_empty
