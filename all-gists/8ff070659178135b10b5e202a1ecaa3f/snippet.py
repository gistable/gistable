import sys, marshal, functools, subprocess

child_script = """
import marshal, sys, types;
fn, args, kwargs = marshal.load(sys.stdin)
marshal.dump(
    types.FunctionType(fn, globals())(*args, **kwargs),
    sys.stdout)
"""

def sudo(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        proc_args = [
            "sudo",
            sys.executable,
            "-c",
            child_script]
        proc = subprocess.Popen(
            proc_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        send_data = marshal.dumps((
            fn.func_code,
            args,
            kwargs))
        recv_data = proc.communicate(send_data)[0]
        return marshal.loads(recv_data)
    return inner

@sudo
def whoami():
    import os
    return "I am: %d" % os.getuid()

if __name__ == '__main__':
    print whoami()