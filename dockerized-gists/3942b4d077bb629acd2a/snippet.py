#!/usr/bin/env python

"""
rerun - kill and rerun subprocess on recieving HUP signal.

$ rerun myproc

In another terminal restart using  
$ kill rerun:myproc -HUP

"""
import sys
import subprocess
import signal
import os
import time
import psutil

from setproctitle import setproctitle

def get_wininfo(p):
    """
    for i in `xlsclients -l | grep "^ *Name" | awk '{print $2}'`; do echo -n "$i "; xprop -name "$i" | grep PID | awk '{print $3}'; done
    """
    import time
    time.sleep(1.0)
    windows = {}
    for line in subprocess.check_output(["/usr/bin/xlsclients", "-l"]).splitlines():
        if not line.startswith("  "):
            wid = int(line[7:-1], 0)
            window = { "wid": wid}
            windows[wid] = window
        else:
            k, v = line[2:].split(':')
            window[k.strip().lower()] = v

    for wid, window in windows.items():
        for line in subprocess.check_output(["/usr/bin/xprop", "-id", "%s" % wid]).splitlines():
            if line.startswith("_NET_WM_PID"):
                pid = int(line.split(" = ")[-1])
                window['pid'] = pid
                if pid == p.pid:
                    return window


should_restart = False
def handle_hup(*args, **kwargs):
    global should_restart, p
    should_restart = True
    os.killpg(p.pid, signal.SIGTERM)

def main():
    if len(sys.argv) == 1:
        print "rerun program [args..]"
        sys.exit(0)
    global should_restart, p
    signal.signal(signal.SIGHUP, handle_hup)
    cmd = sys.argv[1:]
    procname = "rerun:%s" % sys.argv[1]
    setproctitle(procname)
    print("In another terminal restart using")
    print("$ kill rerun:%s -HUP" % procname)
    print("")
    print("running:")
    print(" ".join(cmd))

    while True:
        should_restart = False
        p = subprocess.Popen(" ".join(cmd), shell=True,
                        preexec_fn=os.setsid,
                        )
        ps = psutil.Process(p.pid).children(recursive=True)[0]
        print "-----------------------------------"
        print psutil.Process(p.pid)
        print psutil.Process(p.pid).children(recursive=True)
        win = get_wininfo(ps)
        if win:
            print "win info:"
            print win
        p.wait()
        if not should_restart:
            break
        print("Restart...")

if __name__=="__main__":
    main()
