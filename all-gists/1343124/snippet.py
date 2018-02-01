#!/usr/bin/env python

"""Notifies the user when MPD changes

This script polls mpd and sends out a notification using either pynotify or notify-send whenever either the status of
MPD changes or if a new song is being played. In general, it should work fine without any modifications.
Just run it with python mpd-notify.py. If that doesn't work, read on.

Specify the cover art folder, where downloaded cover images will be
stored, below. You can use pycoverart (http://pycoverart.googlecode.com/svn/trunk/cover_art.py) to download cover art
for your whole collection if necessary, otherwise, this script will download them when needed. If you want to copy the
art to a particular file location - to display it in conky, for example - you can specify a path to that file on line
101.

Note: The daemonizer apparently doesn't work for everyone. If this is the case for you, uncomment line 58
Dependencies:
    - python-mpd
    - python-notify (Optional but highly recommended)
    - python-imaging (Only for conky support)

Get the latest version of the script here: http://mpd.wikia.com/wiki/Hack:mpd-notify.py"""

from __future__ import print_function
import os
import time
import sys
import socket
import glob

try:
    import mpd
except ImportError:
    print("Can't import mpd. Please install the python bindings for MPD (python-mpd or mpd-python)")
    sys.exit(1)

# Try to import pynotify and fall back if we can't
try:
    import pynotify
    pynotify_module = True
except ImportError:
    print("Can't import pynotify so we'll use notify-send instead. We cannot update notifications using this method.")
    pynotify_module = False
try:
    from daemon import daemon as Daemon
    daemon_module = True
except ImportError:
    # We couldn't find the daemon module so we'll try to download it
    import urllib2
    print("This script requires a python module to daemonize notifications. Getting it now.")
    module = urllib2.urlopen("https://raw.github.com/gist/1343075/faac02ebde4f22756857f3dbc2babd001d593303/daemon.py")
    with open(sys.path[0] + "/daemon.py",'wb') as module_file:
        module_file.write(module.read())
    try:
        from daemon import daemon as Daemon
        daemon_module = True
        print("It worked!")
    except ImportError:
        print("It didn't work.")
        # Getting the module failed so fall back to a built in daemonizer
        daemon_module = False

# Uncomment the line below if the daemon module crashes for you.
#daemon_module = False

# Try to import pycoverart and fallback if we can't
try:
    import cover_art
    cover_art_module = True
except ImportError:
    # We couldn't find the coverart module so we'll try to download it
    import urllib2
    print("This script requires a python module to download cover art. Getting it now.")
    module = urllib2.urlopen("http://pycoverart.googlecode.com/svn-history/trunk/cover_art.py")
    with open(sys.path[0] + "/cover_art.py",'wb') as module_file:
        module_file.write(module.read())
    try:
        import cover_art
        cover_art_module = True
        print("It worked!")
    except ImportError:
        print("It didn't work.")
        # Getting the module failed
        cover_art_module = False
try:
    import Image
except ImportError:
    print("Warning: Can't import Image. Please install the Python Imaging Library (probably python-imaging) if you want to use conky to display your cover-art. The cover art will then additionally be copied to a fixed location in your filesystem.")

__author__ = "Durand D'souza"
__email__ = "durand1 [at] gmail [dot] com"
__credits__ = ["Durand D'souza",
               ("Patrick Hirt", "patrick [dot] hirt [at] gmail [dot] com"),
               ("Henning Hollermann", "laclaro [at] mail [dot] com")]
__version__ = "28/07/12"
__license__ = "GPL v3"

# MPD settings
MPD_HOST = "localhost"
MPD_PORT = 6600

# Folder containing album covers. New album arts will be saved to this location as files like "artist-album.ext".
COVERS_FOLDER = "~/.covers"

# Fixed .jpg-file that the cover art should additionally be written to on song change. You can use this to, e.g, display
# the album art with conky. Leave this empty "" to disable.
COVER_ART_CONKY = "/tmp/conky_mpd_cover_art.jpg"

# Time to wait in seconds between checking mpd status changes
POLLING_INTERVAL = 0.5
# Time to wait in seconds between checking for mpd existing
SLEEP_INTERVAL = 5

def sanitize(name):
    """Replaces disallowed characters with an underscore"""
    ## Disallowed characters in filenames
    DISALLOWED_CHARS = "\\/:<>?*|"
    if name == None:
        name = "Unknown"
    for character in DISALLOWED_CHARS:
        name = name.replace(character,'_')
    # Replace " with '
    name = name.replace('"', "'")

    return name

def cover_exists(artist, album, location):
    """Check if a cover exists for a particular album"""
    return glob.glob(u"{0}/{1}-{2}.*".format(location, sanitize(artist), sanitize(album)).replace("[", "\\[").replace("]", "\\]"))

def get_album_cover(artist, album):
    """This function returns a cover image path or an icon if a cover doesn't exist"""
    # If we're allowed to use the cover art module
    if cover_art_module:
        cover_path = cover_art.get_cover(artist, album, os.path.expanduser(COVERS_FOLDER))
        # If it is valid, return it
        if cover_path:
            return cover_path
    # Otherwise, use a simplified approach and don't download new art
    else:
        # Just get what's available
        cover_path = cover_exists(artist, album, os.path.expanduser(COVERS_FOLDER))[0]
        if cover_path:
            return cover_path
    # If an image doesn't exist, return an icon
    return "sonata"


def send_notification(summary, message="", icon=None, update=True):
    """This function takes information and sends a notification to the notification daemon using pynotify or
    notify-send. If update is set to False, a new notification will be created rather than updating the previous one"""
    if icon == None:
        icon = "sonata"

    if pynotify_module:
        global notification
        if update:
            notification.update(summary=summary, message=message, icon=icon)
        else:
            notification = pynotify.Notification(summary=summary, message=message, icon=icon)
        notification.show()
    else:
        # Use notify-send instead
        os.popen('notify-send -i "{0}" "{1}" "{2}"'.format(icon.replace('"', '\\"'), summary.replace('"', '\\"'), message.replace('"', '\\"')))

def observe_mpd(client, log_file):
    """This is the main function in the script. It observes mpd and notifies the user of any changes."""

    if pynotify_module:
        # Initialise notifications
        pynotify.init("icon-summary-body")
        global notification
        notification = pynotify.Notification("MPD notify initialising")
        #notification.show()

    # Loop and detect mpd changes
    last_status = "Initial"
    last_song = "Initial"

    while True:
        # Get status
        current_status = client.status()['state']
        # There might be errors when getting song details if there is no song in the playlist
        try:
            current_song = client.currentsong()['file']
            # Get song details
            artist = client.currentsong()['artist']
            album = client.currentsong()['album']
            title = client.currentsong()['title']
        except KeyError:
            current_song, artist, album, title = ("", "", "", "")

        # If the song or status has changed, notify the user
        if current_status != last_status and last_status != "Initial":
            print("{0}: Status change: {1}".format(time.strftime("%a, %d %b %Y %H:%M:%S"), current_status),
                  file=log_file)
            if current_status == "play": # Not sure how to make this one show in an efficient way so we won't bother
                pass # send_notification(summary="MPD", message="Playing", icon="media-playback-start")
            elif current_status == "pause":
                send_notification(summary="MPD", message="Paused", icon="media-playback-pause")
            else: # Otherwise we assume that mpd has stopped playing completely
                send_notification(summary="MPD", message="Stopped", icon="media-playback-stop")

        if (current_song != last_song and current_song != "") or (current_status != last_status and current_status ==
                                                                  "play") and last_song != "Initial":
            print("{0}: Song change: {1} by {2} in {3}".format(time.strftime("%a, %d %b %Y %H:%M:%S"), title, artist,
                                                               album), file=log_file)
            cover_art = get_album_cover(artist, album)
            send_notification(summary=artist, message=title, icon=cover_art, update=True)
            if COVER_ART_CONKY != "":
               # If we got a cover_art-image copy it to /tmp/ to be able to display it in conky
               if cover_art != "sonata":
                  im = Image.open(cover_art)
                  im.save(COVER_ART_CONKY, "JPEG")
               # else just remove the temporary file
               else:
                   os.remove(COVER_ART_CONKY)

        # Save current status to compare with later
        last_status = current_status
        last_song = current_song
        # Sleep for some time before checking status again
        time.sleep(POLLING_INTERVAL)

def run_notifier(self=None):
    """Runs the notifier"""
    # Opens the log file to send errors to
    log_file = open("/tmp/mpd_notify.log", "w", 0)
    # Initialise mpd client and wait till we have a connection
    while True:
        try:
            client = mpd.MPDClient()
            client.connect(MPD_HOST, int(MPD_PORT))
            print("{0}: Connected to MPD".format(time.strftime("%a, %d %b %Y %H:%M:%S")), file=log_file)
            # Run the observer but watch for mpd crashes
            observe_mpd(client, log_file)
        except KeyboardInterrupt:
            print("\nLater!")
            sys.exit()
        except (socket.error, mpd.ConnectionError):
            print("{0}: Cannot connect to MPD".format(time.strftime("%a, %d %b %Y %H:%M:%S")), file=log_file)
            time.sleep(SLEEP_INTERVAL)

if daemon_module:
    class MPDNotify(Daemon):
        """Daemon class to run notifier"""
        run = run_notifier

def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    """Fork the notification daemon using an alternate method to daemon.py
    Contributed by Patrick Hirt"""
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
            sys.stderr.write('Fork #1 failed: (%d) %s\n' % (e.errno, e.strerror))
            sys.exit(1)

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write('Fork #2 failed: (%d) %s\n' % (e.errno, e.strerror))
        sys.exit(1)

    for f in sys.stdout, sys.stderr:
        f.flush()
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

if __name__ == "__main__":
    if daemon_module:
        # If we are using the daemon module
        daemon = MPDNotify("/tmp/mpd_notify.pid")
        USAGE = "Usage: {0} start|stop|restart".format(sys.argv[0])
    if len(sys.argv) == 2:
        if daemon_module:
            if sys.argv[1] == "start":
                daemon.start()
            elif sys.argv[1] == "stop":
                daemon.stop()
            elif sys.argv[1] == "restart":
                daemon.restart()
            else:
                print("Unknown command")
                print(USAGE)
                sys.exit(2)
            sys.exit(0)
        else:
            if sys.argv[1] == "daemonize":
                # If we don't use the daemon module, just use daemonize()
                daemonize()
                run_notifier()
            else:
                print("""Usage: {0} [daemonize]""".format(sys.argv[0]))

    else:
        if daemon_module:
            print(USAGE)
            sys.exit(2)
        else:
            # Just run the notifier withouth daemonizing
            print("""Couldn't import the daemon module. Get the daemon module from http://is.gd/IXTtnT and save it next\
 to this script or type -h for usage""")
            run_notifier()