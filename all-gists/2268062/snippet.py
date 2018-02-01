import sys, os, termios, tty
pid, fd = os.forkpty()

term_info = termios.tcgetattr(sys.stdin.fileno())

if pid < 0:
    raise ValueError("Early exit: could not fork process")

elif pid == 0:
    # .. child ..
    # .. turn off echo ..
    tty.setraw(sys.stdin.fileno())
    term_info[3] &= ~ (termios.ECHO | termios.ECHOE | termios.ECHOK | termios.ECHONL)
    term_info[2] &= ~ (termios.ONLCR)
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, term_info)
    shell = os.environ.get('SHELL', '/bin/bash')
    os.execl(shell, '')

else:
    # .. parent ..
    xfd = sys.stdin.fileno()
    tty.setraw(xfd)
    pid = os.fork()
    if pid == 0:
        # ..  pipe from fd to stdout ..
        sys.stdout.write('pty started. Type Control-D to exit\n')
        c = os.read(fd, 1)
        while c:
            sys.stdout.write(c)
            sys.stdout.flush()
            c = os.read(fd, 1)

    else:
        # .. pipe from stdin to fd ..
        stdin = sys.stdin.fileno()
        c = os.read(stdin, 1)
        while c:
            os.write(fd, c)
            c = os.read(stdin, 1)
        sys.exit()