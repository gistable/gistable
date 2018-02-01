# -*- encoding: utf-8 -*-
from __future__ import print_function

from enum import Enum


class PrintableValue(object):
    def __init__(self, value, printable_name):
        self.value = value
        self.printable_name = printable_name


class EnumWithName(Enum):

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value.value
        obj.printable_name = value.printable_name
        return obj


class Country(EnumWithName):
    AU = PrintableValue('AU', 'Australia')
    US = PrintableValue('US', 'United States of America')
    CA = PrintableValue('CA', 'Canada')


us = Country('US')

print('Enum name:', us.name)
print('Enum value:', us.value)
print('Printable name:', us.printable_name)


print("US == US:", Country('US') == us)

print("US == CA:", Country('US') == Country('CA'))
