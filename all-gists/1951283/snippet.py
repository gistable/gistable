#!/usr/bin/env python
"""
Compressor wrapper script.
"""
import os
import sys
import re
import argparse
import subprocess
import logging
import signal
import select
import time

logger = logging.getLogger('Compressor.app')
logging.basicConfig(level=logging.INFO)

def watchdog_handler(signum, frame):
    raise RuntimeError("""compressord has encountered an error. Data is not being
                       written to the destination file.""")

if __name__ == '__main__':

    description  = """A sensible Compressor caller which will not return until
                      the destination path file has been created. Arguments are
                      passed through."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-batchname", default="Compressor", help="name to be given to the batch.")
    parser.add_argument("-settingpath", help='url to settings file.', required=True)
    parser.add_argument("-clustername", default="This Computer", help="name of the cluster.")
    parser.add_argument("-jobpath",  help="url to source file.", required=True)
    parser.add_argument("-destinationpath", help="url to destination file.", required=True)

    args = parser.parse_args()

    # Does the destination file already exist? We'll need to check to see if it
    # has been created since after we started.
    start_time = time.time()

    # Ensure that any frameRate specified in the cli is honored by the preferences
    # but setting/adding it to the prefs plist file.
    # looking for: "file:///tmp/085_sub_0010_v999?frameRate=23.976"
    if re.match(".*\?frameRate=.*", args.jobpath):
        frameRate=re.findall("\?frameRate=(.*)$", args.jobpath)[0]
            compressor_plist_file="/home/{0}/Library/Preferences/com.apple.Compressor.plist".format(getpass.getuser())
        try:
            result = subprocess.call(['/usr/libexec/PlistBuddy', '-c',
                             "Set frameRate {0}".format(frameRate),
                             compressor_plist_file])
            if result == 1:
                subprocess.call(['/usr/libexec/PlistBuddy', '-c',
                             "Add frameRate real {0}".format(frameRate),
                             compressor_plist_file])
        except:
            logging.info("Setting preferences went wrong. Skipping.")

    command = ['/Applications/Compressor.app/Contents/MacOS/Compressor',
               '-batchname', args.batchname,
               '-settingpath', args.settingpath,
               '-jobpath', args.jobpath,
               '-destinationpath', args.destinationpath,
               '-clustername', args.clustername]

    logger.info("Calling {0}".format(" ".join(command)))

    # Run the Compressor command and print out the output from Compressor
    # Add TR_PROGRESS if TRACTOR env is True
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    x = p.stdout.fileno()
    while p.poll() is None:
        if select.select([p.stdout], [], [], 0)[0]:
            nAvail = 8192
            line = os.read(x, nAvail)

            logger.info(line)

            # Compressor specific progress to catch in tractor.
            if re.match(".* Compressor\[\d+:\d+] owner is: .*", line):
                if os.getenv('TRACTOR'):
                    print "TR_PROGRESS 33%"
                    sys.stdout.flush()

        time.sleep(0.1)

    # Compressor has returned, but compressord may still be running in the
    # background.
    print "TR_PROGRESS 66%"
    sys.stdout.flush()

    # Exit the process immediatly if Compressor had an exception.
    if p.returncode:
        sys.exit(p.returncode)

    # Assume that compressord will have started up before we get to this point.
    # If it hasn't then the temp file will not have been created and we're s**t
    # out of luck.
    signal.signal(signal.SIGALRM, watchdog_handler)
    tempfile = "{dest}-1".format(dest=args.destinationpath)
    tempfile_size = 0

    while True:
        if os.path.exists(args.destinationpath):
            if os.stat(args.destinationpath).st_mtime > start_time:
                break
        try:
            if tempfile_size:
                updated_size = os.path.getsize(tempfile)
                if updated_size > tempfile_size:
                    signal.alarm(10)
            else:
                tempfile_size = os.path.getsize(tempfile)
                signal.alarm(10)
        except OSError:
            raise RuntimeError("Compressor has not created any output {0}".format(args.destinationpath))

    # All done, clean up the signal alarm and exit cleanly.
    signal.alarm(0)
    print "TR_PROGRESS 85%"
    sys.exit()