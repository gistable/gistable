#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example of `factory method' design pattern
# Copyright (C) 2011 Radek Pazdera

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

class Cup:
    color = ""

    # This is the factory method
    @staticmethod
    def getCup(cupColor):
        if (cupColor == "red"):
            return RedCup()
        elif (cupColor == "blue"):
            return BlueCup()
        else:
            return None

class RedCup(Cup):
    color = "red"

class BlueCup(Cup):
    color = "blue"

# A little testing
redCup = Cup.getCup("red")
print "%s(%s)" % (redCup.color, redCup.__class__.__name__)

blueCup = Cup.getCup("blue")
print "%s(%s)" % (blueCup.color, blueCup.__class__.__name__)

