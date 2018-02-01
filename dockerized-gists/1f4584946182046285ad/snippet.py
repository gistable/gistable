#!/usr/bin/env python

"""
This script compiles and installs Python3 on your CentOS server. 
Built based on the steps described by Digital Ocean (https://www.digitalocean.com/community/tutorials/how-to-set-up-python-2-7-6-and-3-3-3-on-centos-6-4)
"""

import os
import subprocess


def execute_command(*args, **kwargs):
    kwargs['shell'] = True

    try:
        print '-> Running: %s' % ' '.join(args)
        p = subprocess.Popen(*args, **kwargs)
        p.wait()
    except KeyboardInterrupt, e:
        p.terminate()
        # Propagate exception to halt everything
        raise e


def download_python3():
    version = raw_input('''Please enter version of Python3 that you\'d like to install.
                    (see: https://www.python.org/ftp/python/): ''')

    execute_command('wget https://www.python.org/ftp/python/%s/Python-%s.tar.xz' % (version, version))
    execute_command('xz -d Python-%s.tar.xz' % version)
    execute_command('tar -xvf Python-%s.tar' % version)
    execute_command('cd Python-%s; ./configure; make && make altinstall' % version)


def install_development_dependencies():
    execute_command('/usr/bin/yum groupinstall -y "development tools"')
    execute_command('yum install -y openssl-devel sqlite-devel bzip2-devel xz-libs')
    execute_command('yum install -y wget')


def cleanup():
    execute_command('rm Python-*.tar*')
    execute_command('rm -rf Python-*')


def main():
    try:
        install_development_dependencies()
        download_python3()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == '__main__':
    main()

