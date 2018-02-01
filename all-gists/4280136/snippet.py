import os
import subprocess
import shlex


def bail_if_another_is_running():
    cmd = shlex.split("pgrep -u {} -f {}".format(os.getuid(), __file__))
    pids = subprocess.check_output(cmd).strip().split('\n')
    if len(pids) > 1:
        pids.remove("{}".format(os.getpid()))
        print "Exiting! Found {} is already running (pids): {}".format(
            __file__, " ".join(pids))
        raise SystemExit(1)
