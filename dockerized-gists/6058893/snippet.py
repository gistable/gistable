# -*- coding: utf-8 -*-
# champs.py

from __future__ import print_function
import os, os.path
import sys
import re

# log processing

maps = {}
champs = {}

def save_data():
    with open('champ_data.txt', 'w') as f:
        f.write(str(maps) + '\n')
        f.write(str(champs) + '\n')

def load_data():
    global maps, champs
    try:
        with open('champ_data.txt') as f:
            maps = eval(f.readline())
            champs = eval(f.readline())
        return True
    except:
        return False

def increment(map, key):
    map[key] = map.get(key, 0) + 1
    
def add_map(map):
    increment(maps, map)
    
def filter_skin(name):
    i = name.find('(')
    if i > 0:
        return name[:i]
    return name

def add_champ(hero, user):
    userdict = champs.setdefault(user, {'total': 0, 'champs': {}, 'skins': {}})
    userdict['total'] += 1
    
    filtered = filter_skin(hero)
    increment(userdict['champs'], filtered)
    if filtered != hero:
        increment(userdict['skins'], hero)

def read_files(folder):
    files = os.listdir(folder)
    map_expr = re.compile(r'Started Map (.+)')
    champ_expr = re.compile(r'Hero (.+) created for (.+)')

    last_percent = 0
    for i, file in enumerate(files):
        percent = int(100 * i / len(files))
        if int(percent / 10) > int(last_percent / 10):
            last_percent = percent
            print('Completed %2d%%' % percent)
        
        with open(os.path.join(folder, file)) as f:
            lines = f.readlines()
        
        num = 0
        for line in lines:
            match = map_expr.search(line)
            if match:
                add_map(match.group(1))
                continue
            
            match = champ_expr.search(line)
            if match:
                add_champ(match.group(1), match.group(2))
                num += 1
                continue
                
            if 'GAMESTATE_GAMELOOP Begin' in line:
                break
    
    print('Finished reading %d log files' % len(files))

# log analysis

map_names = {
    1: "Summoner's Rift",
    3: 'Proving Grounds',
    4: 'Twisted Treeline (Old)',
    8: 'Crystal Scar',
    10: 'Twisted Treeline',
    12: 'Howling Abyss'
}

def pretty_print(data, most=10):
    keys = sorted(data.keys(), key=data.get, reverse=True)
    maxlen = max(len(k) for k in keys[:most])
    fmt = '%-' + str(maxlen) + 's : %s'
    for k in keys[:most]:
        print(fmt % (k, data[k]))
    return keys[0]

def print_maps():
    print('== Top Maps ==')
    named_maps = {map_names.get(int(k[3:]), k): maps[k] for k in maps.keys()}
    pretty_print(named_maps)
    print()

def print_summoners():
    print('== Top Summoners ==')
    played_with = {k: champs[k]['total'] for k in champs.keys()}
    r = pretty_print(played_with)
    print()
    return r
    
def summoner_stats(name):
    print('== Stats for %s ==' % name)
    user = champs[name]
    print('Total games:', user['total'])
    
    print('Top 10 Champions')
    pretty_print(user['champs'])
    print()
    
    print('Top 10 Skins')
    pretty_print(user['skins'])
    print()

def run_report(folder):
    if load_data():
        print('** Loaded existing data')
    else:
        print('** Parsing log files')
        read_files(folder)
        save_data()
        print('** Saved data for reuse')
        print()
    
    print_maps()
    summoner = print_summoners()
    summoner_stats(summoner)

# main

if __name__ == '__main__':
    run_report("C:\\Riot Games\\League of Legends\\Logs\\Game - R3d Logs")

