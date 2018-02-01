#!/usr/bin/env python
# -*- coding: utf8 -*-
import subprocess

from operator import itemgetter, methodcaller

import dbus


def get_current_track():
    bus = dbus.SessionBus()
    player = bus.get_object('com.spotify.qt', '/')
    iface = dbus.Interface(player, 'org.freedesktop.MediaPlayer2')
    info = iface.GetMetadata()

    if not info:
        return ['']
    else:
        artist = info['xesam:artist'][0]
        title = info['xesam:title']

        return [
            u'♫ {artist} - {title} ♫'.format(artist=artist, title=title).encode('utf8')
        ]


def get_current_state(battery):
    state = ''
    pct = 100.0

    output = subprocess.check_output(
        'upower -i {} | grep -E "state|percentage"'.format(battery), shell=True
    ).strip().split('\n')

    for line in map(methodcaller('strip'), output):
        name, _, data = line.rpartition(' ')

        if 'state' in name:
            state = data
        elif 'percentage' in name:
            pct = float(data.rstrip('%'))

    return state, pct


def as_hearts(percent, factor=10):
    # FIXME: Show 1 full heart for every 10% it has
    heart = u'♥'.encode('utf8')

    num_full = int(round(percent / factor))
    num_empty = (100 / factor) - num_full

    full_hearts = heart * num_full
    empty_hearts = heart * num_empty

    return '#[fg=red,bg=black]{}#[fg=white,bg=black]{}'.format(full_hearts, empty_hearts)


def get_memory():
    total = None
    free = None
    buffers = None
    cached = None

    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                total = float(line.strip().split(' ')[-2])
            elif line.startswith('MemFree:'):
                free = float(line.strip().split(' ')[-2])
            elif line.startswith('Buffers:'):
                buffers = float(line.strip().split(' ')[-2])
            elif line.startswith('Cached:'):
                cached = float(line.strip().split(' ')[-2])

    # Convert to MB
    total /= 1024.0
    free /= 1024.0
    buffers /= 1024.0
    cached /= 1024.0
    used = total - free - buffers - cached
    pct = (used / total) * 100.0

    if pct < 85:
        color = '#[fg=white,bg=black]'
    elif pct < 95:
        color = '#[fg=yellow,bg=black]'
    else:
        color = '#[fg=red,bg=black]'

    kwargs = {
        'color': color,
        'reset': '#[fg=white,bg=black]',
        'free': int(used),
        'total': int(total),
    }

    return ['{color}MEM: {free}/{total}MB{reset}'.format(**kwargs)]


def get_battery(factor=10):
    status = []
    output = subprocess.check_output('upower -e | grep BAT', shell=True).strip().split('\n')
    batteries = map(methodcaller('strip'), output)

    for battery in batteries:
        _, _, name = battery.rpartition('_')
        state, pct = get_current_state(battery)

        if pct > 25:
            color = '#[fg=white,bg=black]'
        elif pct > 15:
            color = '#[fg=yellow,bg=black]'
        else:
            color = '#[fg=red,bg=black]'

        if state == 'charging':
            color = '#[fg=green,bg=black]+'

        status.append((name, as_hearts(pct, factor=factor), color))

    return ['{}{}: {}#[fg=white,bg=black]'.format(c, b, h) for b, h, c in sorted(status, key=itemgetter(0))]


def get_loadavg():
    with open('/proc/loadavg', 'r') as f:
        loadavg = float(f.readline().strip().split(' ')[0])

        if loadavg < 2.5:
            color = '#[fg=white,bg=black]'
        elif loadavg < 5:
            color = '#[fg=yellow,bg=black]'
        else:
            color = '#[fg=red,bg=black]'

        kwargs = {
            'color': color,
            'reset': '#[fg=white,bg=black]',
            'load': '{:.2f}'.format(loadavg),
        }

        return ['{color}LOAD: {load}{reset}'.format(**kwargs)]


def main():
    factor = 20

    lines = []
    lines += get_current_track()
    lines += get_loadavg()
    lines += get_memory()
    lines += get_battery(factor=factor)

    print '{} '.format(' | '.join(lines))


if __name__ == '__main__':
    main()
