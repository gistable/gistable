#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2013 Ben Ockmore

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import musicbrainzngs as mb
import os
import json

def pprint(data):
    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

mb.set_useragent('eac-cue-submit-isrc','1','ben.sput@gmail.com')

user = raw_input("MB Username: ")
pw = raw_input("MB Password: ")
try:
    mb.auth(user,pw)
except mb.AuthenticationError:
    print("Invalid authentication!")

delete_list = []
for directory, directories, filenames in os.walk(u"."):
    for filename in filenames:
        path = os.path.realpath(os.path.join(directory,filename))

        if os.path.splitext(path)[1] != u".cue":
            continue

        print("-------------------------------------------")
        
        print(path)
        release = {}
        tracks = []
        track = {}
        with open(path,"r") as f:
            for line in f:
                if line.startswith('TITLE'):
                    # Release title
                    release['title'] = line.split("\"")[1]
                elif line.startswith('  TRACK'):
                    # Track number
                    track['number'] = int(line.split()[1])
                elif line.startswith('    TITLE'):
                    # Track title
                    track['title'] = line.split("\"")[1]
                elif line.startswith('    ISRC'):
                    # Track title
                    track['isrc'] = line.split()[1]
                
                if ('isrc' in track) and ('number' in track):
                    #Ready to submit
                    print("Submitting {} for track {} on {}".format(track['isrc'],track['number'],release['title']))
                    tracks.append(track)
                    track = {}

        isrcs = []
        for t in tracks:
            if t['isrc'] in isrcs:
                print(u'Duplicate ISRCs - needs further attention')
                break
            else:
                isrcs.append(t['isrc'])
        else:
            #Submit to MB

            #Get user to enter release mbid for release
            release_mbid = raw_input("MBID for {}: ".format(release['title']))
            if release_mbid:
                disc_number = int(raw_input("And the disc number: "))

                release_data = mb.get_release_by_id(release_mbid, includes=['recordings'])

                medium = release_data['release']['medium-list'][disc_number-1]
                upload_data = zip([(t['recording']['id'],t['recording']['title']) for t in medium['track-list']],[(t['title'], t['isrc']) for t in tracks])
                for t in upload_data:
                    print(u"Matching {} to {}".format(t[0][1], t[1][0]))

                confirm = (True if raw_input("Does this look ok? (y/n): ").lower() == 'y' else False)

                if confirm:
                    print("Submitting...")
                    submit_dict = {t[0][0]: [t[1][1]] for t in upload_data}
                    pprint(submit_dict)
                    mb.submit_isrcs(submit_dict)

            delete = (True if raw_input("Delete the CUE file? (y/n): ").lower() == 'y' else False)
            delete_list.append(path)


        print("-------------------------------------------")
        
for f in delete_list:
    os.unlink(f)

print("Done!")
