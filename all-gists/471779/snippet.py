#!/usr/bin/env python

"""Aliases for argparse positional arguments."""

import argparse

class AliasedSubParsersAction(argparse._SubParsersAction):

    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ','.join(aliases)
            sup = super(AliasedSubParsersAction._AliasedPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help) 

    def add_parser(self, name, **kwargs):
        if 'aliases' in kwargs:
            aliases = kwargs['aliases']
            del kwargs['aliases']
        else:
            aliases = []

        parser = super(AliasedSubParsersAction, self).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser
        # Make the help text reflect them, first removing old help entry.
        if 'help' in kwargs:
            help = kwargs.pop('help')
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser

if __name__ == '__main__':
    # An example parser with subcommands.
    
    parser = argparse.ArgumentParser()
    parser.register('action', 'parsers', AliasedSubParsersAction)
    parser.add_argument("--library", metavar="libfile", type=str,
        help="library database filename")
    subparsers = parser.add_subparsers(title="commands", metavar="COMMAND")

    p_import = subparsers.add_parser("import", help="add files to library",
                                     aliases=('imp', 'im'))
    p_import.add_argument("filename", metavar="file", type=str, nargs="+",
        help="the files to import")

    p_remove = subparsers.add_parser("remove", aliases=('rm',),
        help="remove items")
    
    args = parser.parse_args()
    print args
