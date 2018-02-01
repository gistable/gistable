#!/usr/bin/env python

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

import sys, re

class UrtScore:
    # Misc Constants
    SUICIDE_CAUSES = ("MOD_SUICIDE", "MOD_FALLING", "MOD_WATER", "MOD_TRIGGER_HURT")
    KILL_POINT = 2.0
    DEATH_POINT = -0.5
    SUICIDE_POINT = -3.0

    def __init__(self, gamelog):
        self.gamelog = gamelog
        self._game_scores = {}

    def _process_entry(self, target, action):
        if target != "<world>":
            if target in self._game_scores:
                if action == "kill":
                    self._game_scores[target] += self.KILL_POINT
                if action == "death":
                    self._game_scores[target] += self.DEATH_POINT
                if action == "suicide":
                    self._game_scores[target] += self.SUICIDE_POINT
            else:
                if re.search('_\d+$', target):
                    original_target = re.search('(.*)_\d+$', target).groups()[0]
                    self._process_entry(original_target, action)
                else:
                    self._game_scores[target] = 0.0

    def count_scores(self):
        file_handle = open(self.gamelog, 'r')
        for line in file_handle:
            players = re.search("(\S+) killed (\S+) by (\S+)", line)
            if players is not None:
                killer = players.groups()[0]
                victim = players.groups()[1]
                cause = players.groups()[2]
                self._process_entry(killer, "kill")
                if cause in self.SUICIDE_CAUSES:
                    self._process_entry(victim, "suicide")
                else:
                    self._process_entry(victim, "death")
        return self._game_scores


def main():
    if len(sys.argv) == 2:
        score = UrtScore(sys.argv[1])
        all_scores = score.count_scores()
        for entry in all_scores:
        	print "> %-25s: %1.1f" % (entry, all_scores[entry])
    else:
        print "Usage: python urtscore.py /path/to/game.log"


if "__main__" == __name__ : main()