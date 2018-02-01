#!/usr/bin/env python
#
# author: syl20bnr (2013)
# goal: Focus the nth window in the current workspace (limited to 10 firsts)
#
# Example of usage in i3 config:
#
# bindsym $mod+0   exec focus_win.py -n 0
# bindsym $mod+1   exec focus_win.py -n 1
# ...              ...
# bindsym $mod+8   exec focus_win.py -n 8
# bindsym $mod+9   exec focus_win.py -n 9

import argparse
from subprocess import Popen
import i3


PARSER = argparse.ArgumentParser(prog='focus_win')
PARSER.add_argument('-n', '--number',
                    required=True,
                    type=int,
                    choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    help='Window number (limited to [0,9]).')


def focus_nth_window(nth):
    ''' Roughly focus the nth window in the hierarchy (limited to 10 first) '''
    wins = get_windows_from_current_workspace()
    if nth == 0:
        nth = 10
    cmd = 'i3-msg [con_id={0}] focus'.format(wins[nth-1])
    Popen(cmd, shell=True)


def get_windows_from_current_workspace():
    res = []
    ws = get_current_workspace()
    workspace = i3.filter(name=ws)
    if workspace:
        workspace = workspace[0]
        windows = i3.filter(workspace, nodes=[])
        for window in windows:
            res.append(window['id'])
    return res


def get_current_workspace():
    ''' Returns the current workspace '''
    workspaces = i3.msg('get_workspaces')
    workspace = i3.filter(tree=workspaces, focused=True)
    if workspace:
        return workspace[0]['name']
    return ''


if __name__ == '__main__':
    args = PARSER.parse_args()
    focus_nth_window(args.number)
