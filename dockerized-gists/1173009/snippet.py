#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example of `bridge' design pattern
# This code is part of http://wp.me/p1Fz60-8y
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


class AbstractInterface:

    """ Target interface.

    This is the target interface, that clients use.
    """

    def someFunctionality(self):
        raise NotImplemented()


class Bridge(AbstractInterface):

    """ Bridge class.
    
    This class forms a bridge between the target
    interface and background implementation.
    """

    def __init__(self):
        self.__implementation = None


class UseCase1(Bridge):

    """ Variant of the target interface.

    This is a variant of the target Abstract interface.
    It can do something little differently and it can
    also use various background implementations through
    the bridge.
    """
    
    def __init__(self, implementation):
        self.__implementation = implementation

    def someFunctionality(self):
        print "UseCase1: ",
        self.__implementation.anotherFunctionality()


class UseCase2(Bridge):
    def __init__(self, implementation):
        self.__implementation = implementation

    def someFunctionality(self):
        print "UseCase2: ",
        self.__implementation.anotherFunctionality()


class ImplementationInterface:
    
    """ Interface for the background implementation.

    This class defines how the Bridge communicates
    with various background implementations.
    """

    def anotherFunctionality(self):
        raise NotImplemented

class Linux(ImplementationInterface):

    """ Concrete background implementation.

    A variant of background implementation, in this
    case for Linux!
    """

    def anotherFunctionality(self):
        print "Linux!"


class Windows(ImplementationInterface):
    def anotherFunctionality(self):
        print "Windows."


def main():
    linux = Linux()
    windows = Windows()

    # Couple of variants under a couple
    # of operating systems.
    useCase = UseCase1(linux)
    useCase.someFunctionality()

    useCase = UseCase1(windows)
    useCase.someFunctionality()

    useCase = UseCase2(linux)
    useCase.someFunctionality()

    useCase = UseCase2(windows)
    useCase.someFunctionality()


if __name__ == "__main__":
    main()

