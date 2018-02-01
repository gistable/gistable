# -*- coding: utf-8 -*-
"""A convenience wrapper for RawConfigParser."""

import shlex

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser


__all__ = ('ConfigParser',)


class ConfigParser(RawConfigParser):
    """A simple wrapper for RawConfigParser to make options access easier."""

    def get(self, section, option, default=None, **kwargs):
        """
        Return value of option in given configuration section as a string.

        If option is not set, return default instead (defaults to None).

        """
        return (RawConfigParser.get(self, section, option, **kwargs)
                if self.has_option(section, option) else default)

    def getint(self, section, option, default=None):
        """
        Return value of option in given configuration section as an integer.

        If option is not set, return default instead (defaults to None).

        """
        val = self.get(section, option, default)
        return val if val is None else int(val)

    def getfloat(self, section, option, default=None):
        """
        Return value of option in given configuration section as a float.

        If option is not set, return default instead (defaults to None).

        """
        val = self.get(section, option, default)
        return val if val is None else float(val)

    def getboolean(self, section, option, default=False):
        """
        Return value of option in given configuration section as a boolean.

        A configuration option is considered true when it has one of the
        following values: '1', 'on', 'true' or 'yes'. The comparison is
        case-insensitive. All other values are considered false.

        If option is not set, return default instead (defaults to False).

        """
        val = self.get(section, option)
        return default if val is None else val.lower() in (
            '1', 'on', 'true', 'yes')

    def getlist(self, section, option, default=None):
        """
        Return value of option in given section as a list of strings.

        If option is not set, return default (defaults to an empty list).

        The option value is split into list tokens using one of two strategies:

        * If the value contains any newlines, i.e. it was written in the
          configuration file using continuation lines, the value is split at
          newlines and empty items are discarded.
        * Otherwise, the value is split according to unix shell parsing rules.
          Items are separated by whitespace, but items can be enclosed in
          single or double quotes to preserve spaces in them.

        Example::

            [test]
            option2 =
                one
                two three
                four
                sive six
            option1 = one  "two three" four 'five  six'

        """
        if not self.has_option(section, option):
            return [] if default is None else default

        value = self.get(section, option)

        if '\n' in value:
            return [item for item in value.splitlines() if item]
        else:
            return shlex.split(value)

    def set(self, section, option, value):
        """
        Set option in given configuration section to value.

        If section does not exist yet, it is added implicitly.

        """
        if not self.has_section(section):
            self.add_section(section)

        RawConfigParser.set(self, section, option, value)
