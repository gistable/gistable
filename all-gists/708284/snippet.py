#!/usr/bin/env python
import os, re, subprocess, sys
from xml.etree import ElementTree

retag = sys.argv[1] == "retag"
if retag:
    del sys.argv[1]

source = os.path.abspath(sys.argv[1])
extensionless = '.'.join(source.split('.')[:-1])
dest =  extensionless + '.m4v'

if not os.path.exists(dest):
    subprocess.check_call(["HandBrakeCLI", "-i", source, "-o", dest, "--preset", 'AppleTV'])
elif not retag:
    print "Output already exists at", dest
    sys.exit(0)
else:
    print "Retagging", dest

nfo = extensionless + ".nfo"
season = episode = title = plot = None
if os.path.exists(nfo):
    epi = ElementTree.parse(open(nfo))
    if 'xbmcmultiepisode' in epi.getroot().tag:
        epi = epi.find("episodedetails")
    season = epi.findtext("season")
    episode = epi.findtext("episode")
    title = epi.findtext("title")
    plot = epi.findtext("plot")
    if season is None or episode is None or title is None or plot is None:
        print ".nfo Missing item: %s %s %s" % (season, episode, title)
else:
    print "No .nfo, trying to extract from title"
    m = re.match(".* - (\d+)x(\d+) - (.*)\.[\w\d]{3}", source)
    if m:
        season, episode, title = m.groups()
    else:
        print "Couldn't match", source
srcdir = os.path.dirname(source)
# Always mark it as a TV show and name it.  Add the other fields if they're avialable
command = ["AtomicParsley",  dest, "--stik", 'TV Show', "--TVShowName", os.path.basename(srcdir)]
for flag, value in [("--TVSeasonNum", season), ("--TVEpisodeNum", episode), ("--TVEpisode", title),
        ("--title", title), ("--description", plot)]:
    if value is not None:
        command.append(flag)
        command.append(value)
subprocess.check_call(command)
tmp = [i for i in os.listdir(srcdir) if "-temp" in i]
assert len(tmp) == 1
os.rename(srcdir + "/" + tmp[0], dest)

os.system("""osascript << EOF
tell application "iTunes"
    launch
    with timeout of 30000 seconds
        add ("%s" as POSIX file)
    end timeout
end tell
EOF""" % dest)
