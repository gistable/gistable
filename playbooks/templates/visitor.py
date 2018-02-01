"""Parser Visitor."""


# Imports
import ast
import imp
import os
import sys


class ParserVisitor(ast.NodeVisitor):
    """An AST NodeVisitor for library calls."""

    def __init__(self):
        """Initialize CallVisitor."""

        # Encoutered calls
        self.import_names = set()
        self.import_libraries = set()
        self.prefixes = {}
        self.aliases = {}
        self.calls = set()

    def is_standard_library(self, name):
        """Determine if a module name refers to a module in the python standard library.

        Parameters
        ----------
        name : string
            Name of the module to check.

        Returns
        -------
        bool
            True iff the module is in the standard library.
        """

        # Attempt to use python import tools to discover facts about the module.
        # If we get an import error, it was definitely not part of the standard library, so return false.
        # If we do find the module, check to make sure it's not not a builtin or part of python extras or site-packages.
        try:
            path = imp.find_module(name)[1]
            return bool(imp.is_builtin(name) or ('site-packages' not in path and 'Extras' not in path))
        except ImportError:
            return False

    def visit_Import(self, node):
        """Visit import statements.

        Tracks asnames as encountered aliases.
        Adds either the asname or name as an import name.
        """
        for alias in node.names:
            if alias.asname is not None:
                self.aliases[alias.asname] = alias.name
                self.import_names.add(alias.asname)
            else:
                self.import_names.add(alias.name)

            if not self.is_standard_library(alias.name):
                self.import_libraries.add(alias.name)

        # Call generic visit to visit all child nodes
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit import from statements.

        Tracks asnames as encountered aliases.
        Tracks modules as encountered prefixes.
        Adds either the asname or name as an import name.
        """
        for alias in node.names:
            if alias.asname is not None:
                self.aliases[alias.asname] = alias.name
                self.import_names.add(alias.asname)
            else:
                self.import_names.add(alias.name)

            if not self.is_standard_library(node.module):
                self.import_libraries.add(node.module)
                self.prefixes[alias.name] = node.module

        # Call generic visit to visit all child nodes
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit Assign statements.

        If the value of an assignment matches an imported name,
        then treat the targets of the assignment as aliases.
        """
        if type(node.value) is ast.Name and node.value.id in self.import_names:
            for target in node.targets:
                self.aliases[target.id] = node.value.id

        # Call generic visit to visit all child nodes
        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit a Call node.

        Parameters
        ----------
        node : Call
            A Call node in the ast.
        """

        # Add call node to encountered calls
        self.calls.add(self.call_to_string(node))

        # Call generic visit to visit all child nodes
        self.generic_visit(node)

    def call_to_string(self, node):
        """Convert a Call node to a string.

        Parameters
        ----------
        node : Call
            AST Call node.

        Returns
        -------
        string
            String representation of the call
        """
        prefix, suffix = self.get_call_function_segments(node.func)

        if prefix in self.aliases:
            prefix = self.aliases[prefix]

        if prefix in self.prefixes:
            prefix = '{}.{}'.format(self.prefixes[prefix], prefix)

        return '{}{}'.format(prefix, suffix)

    def get_call_function_segments(self, call):
        """Get (prefix, suffix) of function calls."""

        # Get type
        t = type(call)

        if t is ast.Name:
            return (call.id, '')
        elif t is ast.Attribute:
            prefix, suffix = self.get_call_function_segments(call.value)
            return (
                prefix,
                '{}.{}'.format(suffix, call.attr)
                if suffix is not None
                else call.attr
            )
        elif t is ast.Call:
            return self.get_call_function_segments(call.func)
        else:
            return (t.__name__.lower(), '')
