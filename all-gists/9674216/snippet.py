#! /usr/bin/env python

# Copyright 2014 Alex Wood
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Place this file in ~/.config/xchat2 and XChat will auto-load it.

import time
import xchat

__module_name__ = "hush"
__module_version__ = "1.1"
__module_description__ = "Disables joins, nick changes, and quits from inactive users"


class Hush(object):
    def __init__(self, interval=15 * 60):
        self.hooks = []
        self.active_users = {}
        self.interval = interval

    def notice(self, text):
        xchat.emit_print("Server Notice", text, "Hush")

    def toggle_cb(self, word, word_eol, userdata):
        if len(word) < 2 or word[1].lower() not in ['on', 'off', 'status']:
            self.notice("Please provide a command: 'on', 'off', or 'status'")
            return xchat.EAT_ALL

        command = word[1].lower()
        if command == "on":
            if self.hooks:
                self.notice("Hush is already on")
                return xchat.EAT_ALL

            for event in ["Join", "Part", "Part with Reason", "Quit", "Change Nick"]:
                self.hooks.append(xchat.hook_print(event, self.selective_hush_cb))

            for event in ["Private Message", "Private Action", "Channel Message", "Channel Action"]:
                self.hooks.append(xchat.hook_print(event, self.record_cb))

            self.hooks.append(xchat.hook_timer(5 * 60 * 1000, self.reaper_cb))
            self.notice("Loaded Hush")

            return xchat.EAT_ALL
        elif command == "off":
            if self.hooks:
                map(xchat.unhook, self.hooks)
                self.hooks = []
                self.active_users = []
                self.notice("Unloaded Hush")
            else:
                self.notice("Hush is already off")
            return xchat.EAT_ALL
        elif command == "status":
            status = {True: "on", False: "off"}
            self.notice("Hush is %s" % status[bool(self.hooks)])
            return xchat.EAT_ALL

    def selective_hush_cb(self, word, word_eol, userdata):
        user = word[0]
        if user in self.active_users:
            return xchat.EAT_NONE
        return xchat.EAT_XCHAT

    def record_cb(self, word, word_eol, userdata):
        user = word[0]
        self.active_users[user] = int(time.time())
        return xchat.EAT_NONE

    def reaper_cb(self, userdata):
        one_interval_ago = int(time.time()) - self.interval
        dead_users = filter(lambda pair: pair[1] < one_interval_ago, self.active_users.iteritems())
        dead_users = (x[0] for x in dead_users)
        for dead in dead_users:
            del self.active_users[dead]

        # Keep the timer running
        return True


hush = Hush()
# TODO Maybe make the interval configurable
xchat.hook_command("HUSH", hush.toggle_cb,
    help="/HUSH <on|off|status> Disables joins, nick changes, and quits from inactive users.")
hush.toggle_cb(['HUSH', 'on'], None, None)
