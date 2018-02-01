import sys
import os
import math
import urllib2
import json
import time
import shutil
import uuid
from nbt import nbt # pip install nbt

def convert(path):
    if not os.path.isdir(path):
        sys.stderr.write('Path is not directory or does not exist:' + path)
        return False
    max_payload_size = 50
    retry_delay = 3
    profile_url = 'https://api.mojang.com/profiles/minecraft'
    #profile_url = 'http://api.goender.net/api/profiles/minecraft'
    player_data_path = os.path.join(path, 'players')
    target_data_path = os.path.join(path, 'playerdata')
    missing_data_path = os.path.join(path, 'players.missing')
    converted_data_path = os.path.join(path, 'players.converted')
    invalid_data_path = os.path.join(path, 'players.invalid')
    player_files = {}
    if not os.path.isdir(missing_data_path):
        os.mkdir(missing_data_path)
    if not os.path.isdir(converted_data_path):
        os.mkdir(converted_data_path)
    if not os.path.isdir(invalid_data_path):
        os.mkdir(invalid_data_path)
    for player_file in os.listdir(player_data_path):
        if os.path.isfile(os.path.join(player_data_path, player_file)) and player_file.endswith('.dat'):
            name = os.path.splitext(os.path.basename(player_file))[0].lower()
            player_files[name] = os.path.join(player_data_path, player_file)
    if not player_files:
        sys.stderr.write('No player data found!\n')
        return False
    if not os.path.isdir(target_data_path):
        os.mkdir(target_data_path)
    payload = []
    current = 0
    for name in player_files.keys():
        current = current + 1
        payload.append(name)
        if (float(current) % max_payload_size) != 0 and current != len(player_files):
            continue
        request = urllib2.Request(profile_url, json.dumps(payload), {'Content-Type': 'application/json'})
        retry = False
        retry_count = 0
        while True:
            try:
                response = urllib2.urlopen(request)
                if retry:
                    sys.stderr.write('Retry successful! Number of retries: ' + str(retry_count) + '\n')
                    retry = False
                retry_count = 0
                break
            except Exception as e:
                sys.stderr.write(str(e) + " (don't worry, we'll retry until it works!)\n")
                retry = True
                time.sleep(retry_delay)
            retry_count = retry_count + 1
        profiles = json.loads(response.read())
        if isinstance(profiles, dict): # http://api.goender.net/api/profiles/minecraft
            data = profiles
            profiles = []
            for name in data.keys():
                profiles.append({'id': data[name], 'name': name})
        if len(profiles) != len(payload):
            payload_names = set([name.lower() for name in payload])
            response_names = set([profile['name'].lower() for profile in profiles])
            missing_names = list(payload_names - response_names)
            for name in missing_names:
                try:
                    src = player_files[name]
                    shutil.move(src, os.path.join(missing_data_path, os.path.basename(src)))
                except Exception as e:
                    sys.stderr.write('Error moving file file: ' + src + ' (' + str(e) + ')\n') 
            sys.stderr.write('Missing profiles from API response: ' + repr(missing_names) + '\n')
        payload = []
        for profile in profiles:
            name = profile['name'].lower()
            if name not in player_files:
                continue
            src = player_files[name]
            dst = os.path.join(target_data_path, str(uuid.UUID(profile['id'])) + '.dat')
            try:
                nbtfile = nbt.NBTFile(src, 'rb')
            except Exception as e:
                sys.stderr.write('Error reading NBT file: ' + src + ' (' + str(e) + ')\n')
                try:
                    shutil.move(src, os.path.join(invalid_data_path, os.path.basename(src)))
                except:
                    pass
                continue
            try:
                bukkit = nbtfile['bukkit']
            except KeyError:
                bukkit = nbt.TAG_Compound()
                bukkit.name = 'bukkit'
                nbtfile.tags.append(bukkit)
            try:
                lastKnownName = bukkit['lastKnownName']
            except KeyError:
                lastKnownName = nbt.TAG_String(name='lastKnownName')
                bukkit.tags.append(lastKnownName)
            lastKnownName.value = profile['name']
            nbtfile.write_file(dst)
            try:
                shutil.move(src, os.path.join(converted_data_path, os.path.basename(src)))
            except Exception as e:
                sys.stderr.write('Error moving file file: ' + src + ' (' + str(e) + ')\n') 
    return True

if __name__ == '__main__':
    path = 'world'
    if len(sys.argv) > 1:
        path = sys.argv[1]
    if convert(path):
        print 'Player data has been successfully converted.'
