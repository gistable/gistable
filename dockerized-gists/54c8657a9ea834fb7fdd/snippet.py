#!/usr/bin/env python3

import os
import sys

_b = sys.version_info[0] < 3 and (lambda x:x) or (lambda x:x.encode('utf-8'))

def ssh_exec_pass(password, args, capture_output=False):
    '''
        Wrapper around openssh that allows you to send a password to
        ssh/sftp/scp et al similar to sshpass.
        
        Not super robust, but works well enough for most purposes. Typical
        usage might be::
        
            ssh_exec_pass('p@ssw0rd', ['ssh', 'root@1.2.3.4', 'echo hi!'])
        
        :param args: A list of args. arg[0] must be the command to run.
        :param capture_output: If True, suppresses output to stdout and stores
                               it in a buffer that is returned
        :returns: (retval, output)
        
        *nix only, tested on linux and OSX. Python 2.7 and 3.3+ compatible.
    '''

    import pty, select
    
    # create pipe for stdout
    stdout_fd, w1_fd = os.pipe()
    stderr_fd, w2_fd = os.pipe()
    
    pid, pty_fd = pty.fork()
    if not pid:
        # in child
        os.close(stdout_fd)
        os.close(stderr_fd)
        os.dup2(w1_fd, 1)    # replace stdout on child
        os.dup2(w2_fd, 2)    # replace stderr on child
        os.close(w1_fd)
        os.close(w2_fd)
        
        os.execvp(args[0], args)
    
    os.close(w1_fd)
    os.close(w2_fd)
    
    output = bytearray()
    rd_fds = [stdout_fd, stderr_fd, pty_fd]
    
    def _read(fd):
        if fd not in rd_ready:
            return 
        try:
            data = os.read(fd, 1024)
        except (OSError, IOError):
            data = None
        if not data:
            rd_fds.remove(fd) # EOF
            
        return data
    
    # Read data, etc
    try:
        while rd_fds:
            
            rd_ready, _, _ = select.select(rd_fds, [], [], 0.04)
            
            if rd_ready:
                
                # Deal with prompts from pty
                data = _read(pty_fd)
                if data is not None:
                    if b'assword:' in data:
                        os.write(pty_fd, _b(password + '\n'))
                    elif b're you sure you want to continue connecting' in data:
                        os.write(pty_fd, b'yes\n')
                
                # Deal with stdout
                data = _read(stdout_fd)
                if data is not None:
                    if capture_output:
                        output.extend(data)
                    else:
                        sys.stdout.write(data.decode('utf-8', 'ignore'))
                        
                data = _read(stderr_fd)
                if data is not None:
                    sys.stderr.write(data.decode('utf-8', 'ignore'))
    finally:
        os.close(pty_fd)
        
    pid, retval = os.waitpid(pid, 0)
    return retval, output

if __name__ == '__main__':
    retval, _ = ssh_exec_pass(sys.argv[1], sys.argv[2:], False)
    exit(retval)
