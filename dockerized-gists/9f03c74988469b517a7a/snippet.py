'''A simple utility for running UNIX shell commands'''

KEEP_STDOUT = 0x1
KEEP_STDERR = 0x1 << 1
ECHO_STDOUT = 0x1 << 2
ECHO_STDERR = 0x1 << 3


def shell(command, input_=None, output_=(KEEP_STDOUT | KEEP_STDERR | ECHO_STDOUT | ECHO_STDERR), wait=True):
    '''
        Runs a shell command

        command - The bash command to run
        input_ - The input to send to the command (default None)
        output_ - A set of options for what to do with the output.
            KEEP_STDOUT causes stdout to be returned in the first value of the return tuple
            KEEP_STDERR causes stderr to be returned in the second value of the return tuple
            ECHO_STDOUT causes stdout to be repeated to sys.stdout
            ECHO_STDERR causes stderr to be repeated to sys.stderr
        wait - Whether shell should block until the command finishes

        returns stdout, stderr, returncode

        if KEEP_STDOUT is not set or wait=False then stdout is ''
        if KEEP_STDERR is not set or wait=False then stderr is ''
        if wait=False then returncode is 0
    '''
    import subprocess
    import sys
    import select

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True
    )

    sout_fd = process.stdout.fileno()
    serr_fd = process.stderr.fileno()

    so = ''
    se = ''
    if input_ is not None:
        process.stdin.write(input_)
        process.stdin.close()
    if wait:
        while process.poll() is None:
            fds, _, _ = select.select([sout_fd, serr_fd], [], [], .1)
            if sout_fd in fds:
                new_so = process.stdout.readline()
                if output_ & ECHO_STDOUT:
                    sys.stdout.write(new_so)
                if output_ & KEEP_STDOUT:
                    so += new_so
            if serr_fd in fds:
                new_se = process.stderr.readline()
                if output_ & ECHO_STDERR:
                    sys.stderr.write(new_se)
                if output_ & KEEP_STDERR:
                    se += new_se

        new_so = process.stdout.read()
        if output_ & ECHO_STDOUT:
            sys.stdout.write(new_so)
        if output_ & KEEP_STDOUT:
            so += new_so

        new_se = process.stderr.read()
        if output_ & ECHO_STDERR:
            sys.stderr.write(new_se)
        if output_ & KEEP_STDERR:
            se += new_se

        rc = process.returncode
        return so, se, rc
    else:
        return '', '', 0
