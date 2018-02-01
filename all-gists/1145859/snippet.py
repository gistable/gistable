#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example of `adapter' design pattern
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


# Adaptee (source) interface
class EuropeanSocketInterface:
    def voltage(self): pass
    
    def live(self): pass
    def neutral(self): pass
    def earth(self): pass

# Adaptee
class Socket(EuropeanSocketInterface):
    def voltage(self):
        return 230

    def live(self):
        return 1

    def neutral(self):
        return -1

    def earth(self):
        return 0

# Target interface
class USASocketInterface:
    def voltage(self): pass
    
    def live(self): pass
    def neutral(self): pass

# The Adapter
class Adapter(USASocketInterface):
    __socket = None

    def __init__(self, socket):
        self.__socket = socket

    def voltage(self):
        return 110

    def live(self):
        return self.__socket.live()

    def neutral(self):
        return self.__socket.neutral()

# Client
class ElectricKettle:
    __power = None

    def __init__(self, power):
        self.__power = power

    def boil(self):
        if self.__power.voltage() > 110:
            print "Kettle on fire!"
        else:
            if self.__power.live()    == 1 and \
               self.__power.neutral() == -1:
                print "Coffee time!"
            else:
                print "No power."


def main():
    # Plug in
    socket  = Socket()
    adapter = Adapter(socket)
    kettle  = ElectricKettle(adapter)

    # Make coffee
    kettle.boil()

    return 0

if __name__ == "__main__":
    main()
