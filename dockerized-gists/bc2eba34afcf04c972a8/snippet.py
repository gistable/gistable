import os
import subprocess

# Currently only supports CPython
linkto = '/usr/local/bin'

devnull = open(os.devnull, 'w')

if os.path.isdir(os.path.expanduser('~/.pyenv')):
    for major in [2, 3]:
        for minor in range(10):
            executable = 'python' + '.'.join([str(major), str(minor)])
            if subprocess.call(['which', executable], stdout=devnull, stderr=devnull) != 0:
                for patch in reversed(range(11)):
                    execpath = '~/.pyenv/versions/' + '.'.join([str(major), str(minor), str(patch)]) + '/bin/' + executable
                    if os.path.isfile(os.path.expanduser(execpath)):
                        dest = linkto + '/' + executable
                        print(execpath + ' -> ' + dest)
                        os.symlink(os.path.expanduser(execpath), dest)
                        break
else:
    print('Couldn\'t find a pyenv installation')
