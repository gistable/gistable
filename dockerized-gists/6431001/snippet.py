import sys
import subprocess

# Requirements:
# - `adb` command locally
# - `su` command on device

def use_su(cmd):
    to_escape = ['*', '|']

    for char in to_escape:
        cmd = cmd.replace(char, '\\' + char)

    return [ 'shell', 'echo %s | su' % cmd ]

def call_adb():
    if sys.argv[1] == 'root':
        return

    # TODO: 'push' && 'pull'

    if sys.argv[1] == 'remount':
        args = use_su('mount -o rw,remount /system')
    elif sys.argv[1] == 'shell':
        args = use_su(' '.join(sys.argv[2:]))
    else:
        args = sys.argv[1:]

    args.insert(0, 'adb')

    # print args
    subprocess.check_call(args, stdout=sys.stdout, stderr=sys.stderr)

if __name__ == '__main__':
    call_adb()
