#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fortran namelist parser. Converts nameslists to python dictionaries.

Should be fairly robust. Cannot be used for verifying fortran namelists as it
is rather forgiving.

Error messages during parsing are kind of messy right now.

Usage
=====

>>> from namelist import namelist2dict
>>> namelist_dict = namelist2dict("fortran_list.txt")

Can deal with filenames, open files and file-like object (StringIO).


Works with Python 2.7 and has not further dependencies.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013

:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from StringIO import StringIO
import unittest

QUOTE_CHARS = ["'"]


class Token(object):
    """
    Base class for all token types.
    """
    def __str__(self):
        name = self.__class__.__name__
        if hasattr(self, "value"):
            return "%s(%s)" % (name, str(self.value))
        return name

    def __repr__(self):
        return self.__str__()


class StringToken(Token):
    def __init__(self, value):
        self.value = value


class AssignmentToken(Token):
    pass


class GroupEndToken(Token):
    pass


class GroupStartToken(Token):
    def __init__(self, value):
        self.value = value


class IntegerToken(Token):
    def __init__(self, value):
        self.value = int(value)


class FloatToken(Token):
    def __init__(self, value):
        self.value = float(value)


class BooleanToken(Token):
    def __init__(self, value):
        self.value = bool(value)


class NameToken(Token):
    def __init__(self, value):
        self.value = str(value)


class ComplexNumberToken(Token):
    def __init__(self, real, imag):
        self.value = complex(real, imag)


def auto_token(value):
    """
    Instantiates the correct token type based on the passed value string.
    """
    value = value.strip()
    if value.startswith("&"):
        return GroupStartToken(value[1:])
    elif value.lower() == ".true.":
        return BooleanToken(True)
    elif value.lower() == ".false.":
        return BooleanToken(False)
    try:
        return IntegerToken(int(value))
    except:
        pass
    try:
        return FloatToken(float(value))
    except:
        pass
    return NameToken(value)


def tokenizer(file_object):
    """
    The lexer - a generator yielding tokens.
    """
    for line in file_object:
        line = line.strip()
        if not line:
            continue
        in_string = False
        in_complex_number = False
        current_token = []
        for letter in line:
            # Handle strings.
            if letter in QUOTE_CHARS:
                if in_string is True:
                    in_string = False
                    if current_token:
                        yield StringToken("".join(current_token))
                        current_token = []
                else:
                    in_string = True
                continue
            elif in_string is True:
                current_token.append(letter)

            # Handle complex numbers.
            elif letter == "(":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                in_complex_number = True
            elif letter == ")":
                # Parse the complex number.
                real, imag = map(float, "".join(current_token).split(","))
                yield ComplexNumberToken(real, imag)
                current_token = []
                in_complex_number = False
            elif in_complex_number is True:
                current_token.append(letter)

            # Everything from now on is neither string nor complex number.
            elif letter == "!":
                break
            elif not letter.strip():
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
            elif letter == ",":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
            elif letter == "=":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                yield AssignmentToken()
            elif letter == "/":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                yield GroupEndToken()
            else:
                current_token.append(letter)
        if current_token:
            yield auto_token("".join(current_token))


def group_generator(tokens):
    """
    Generator yielding one dictionary per found group.
    """
    current_group = {}
    current_group_name = None
    current_assignment = []
    for token in tokens:
        if isinstance(token, GroupStartToken):
            if current_group_name:
                msg = "Starting new group without ending old one."
                raise ValueError(msg)
            current_group_name = token.value
            continue
        elif isinstance(token, GroupEndToken):
            if current_assignment:
                parse_assignment(current_assignment, current_group)
                current_assignment = []
            if current_group and current_group_name:
                yield (current_group_name, current_group)
            else:
                msg = "Invalid group found."
                raise ValueError(msg)
            current_group = {}
            current_group_name = None
            continue
        elif isinstance(token, NameToken):
            if current_assignment:
                parse_assignment(current_assignment, current_group)
                current_assignment = []
        current_assignment.append(token)


def parse_assignment(assignment,  group):
    """
    Parses all tokens for one assignment. Will write the result to the passed
    group dictionary.
    """
    if len(assignment) < 3:
        msg = "Invalid assignment."
        raise ValueError(msg)
    if not isinstance(assignment[0], NameToken):
        msg = "Assignment must start with a name."
        raise ValueError(msg)
    if not isinstance(assignment[1], AssignmentToken):
        msg = "Assignment must contain an AssignmentToken."
        raise ValueError(msg)
    values = assignment[2:]
    value_types = set([type(_i) for _i in values])
    if len(value_types) != 1:
        msg = "All values for one assignment must have the same type."
        raise ValueError(msg)
    values = [_i.value for _i in values]
    if len(values) == 1:
        values = values[0]
    group[assignment[0].value] = values


def namelist2dict(file_or_file_object):
    """
    Thin wrapper to be able to deal with file-like objects and filenames.
    """
    if hasattr(file_or_file_object, "read"):
        return _namelist2dict(file_or_file_object)
    with open(file_or_file_object, "r") as open_file:
        return _namelist2dict(open_file)


def _namelist2dict(file_object):
    """
    Converts a file_object containng a namelist to a dictionary.
    """
    namelist_dict = {}
    for group_name, group_values in group_generator(tokenizer(file_object)):
        namelist_dict.setdefault(group_name, [])
        namelist_dict[group_name].append(group_values)
    return namelist_dict


class NameListTestCase(unittest.TestCase):
    """
    Some very basic test cases.
    """
    def test_simple_group(self):
        """
        Test simple namelist group with values of different types.
        """
        group = (
            "&group\n"
            "    float = 0.75\n"
            "    integer = 700\n"
            "    string = 'test'\n"
            "    true = .TRUE.\n"
            "    false = .FALSE.\n"
            "/")
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict,
            {"group": [{
                "float": 0.75,
                "integer": 700,
                "string": "test",
                "true": True,
                "false": False
            }]})

    def test_complex_single_line_group(self):
        """
        Tests a rather complex single line group.
        """
        group = "&list a=1, b=1,2 c='12 / !' / "
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict,
            {"list": [{
                "a": 1,
                "b": [1, 2],
                "c": "12 / !"
            }]})

    def test_complex_multiple_group(self):
        """
        Same as test_complex_single_line_group() just split over lines.
        """
        group = (
            "&list a=1\n"
            "b=1,2, c='12 / !' /")
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict,
            {"list": [{
                "a": 1,
                "b": [1, 2],
                "c": "12 / !"
            }]})

    def test_complex_numbers(self):
        """
        Tests complex numbers. Complex number parsing is rather forgiving.
        """
        group = (
            "&complex_group\n"
            "    number_a = (1,2)\n"
            "    number_b = (1.2,3.4)\n"
            "    number_c = (-1.2,0.0)\n"
            "    number_d = (0.0, 1.0)\n"
            "/")

        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict,
            {"complex_group": [{
                "number_a": 1.0 + 2.0j,
                "number_b": 1.2 + 3.4j,
                "number_c": -1.2 + 0.0j,
                "number_d": 0.0j + 1.0j
            }]})

    def test_group_mixed_and_lists(self):
        """
        Tests a real world example.
        """
        group = (
            "&receiver\n"
            "    station ='XX02'\n"
            "    location = 'a'\n"
            "    lon = 12.51\n"
            "    lat = -0.01\n"
            "    depth = 1.0\n"
            "    attributes = 'vx' 'vy' 'vz'\n"
            "    file_name_prefix = './DATA/mess/'\n"
            "    override = .TRUE.\n"
            "/\n")
        namelist_dict = namelist2dict(StringIO(group))
        self.assertEqual(namelist_dict,
            {"receiver": [{
                "station": "XX02",
                "location": "a",
                "lon": 12.51,
                "lat": -0.01,
                "depth": 1.0,
                "attributes": ["vx", "vy", "vz"],
                "file_name_prefix": "./DATA/mess/",
                "override": True
            }]})

    def test_multiple_groups(self):
        """
        Mixes groups from some of the previous tests.
        """
        group = (
            "&group\n"
            "    float = 0.75\n"
            "    integer = 700\n"
            "    string = 'test'\n"
            "    true = .TRUE.\n"
            "    false = .FALSE.\n"
            "/\n"
            "\n"
            "&list a=1, b=1,2 c='12 / !' / \n"
            "&list a=1\n"
            "b=1,2, c='12 / !' /\n"
            "&receiver\n"
            "    station ='XX02'\n"
            "    location = 'a'\n"
            "    lon = 12.51\n"
            "    lat = -0.01\n"
            "    depth = 1.0\n"
            "    attributes = 'vx' 'vy' 'vz'\n"
            "    file_name_prefix = './DATA/mess/'\n"
            "    override = .TRUE.\n"
            "/\n")
        namelist_dict = namelist2dict(StringIO(group))

        self.assertEqual(namelist_dict,
            {"group": [{
                "float": 0.75,
                "integer": 700,
                "string": "test",
                "true": True,
                "false": False
            }],
            "list": [{
                "a": 1,
                "b": [1, 2],
                "c": "12 / !"
                }, {
                "a": 1,
                "b": [1, 2],
                "c": "12 / !"
            }],
            "receiver": [{
                "station": "XX02",
                "location": "a",
                "lon": 12.51,
                "lat": -0.01,
                "depth": 1.0,
                "attributes": ["vx", "vy", "vz"],
                "file_name_prefix": "./DATA/mess/",
                "override": True
            }]})

    def test_real_world_example(self):
        """
        Tests example from
            http://owen.sj.ca.us/~rk/howto/slides/f90model/slides/namelist.html
        """
        groups = (
            "! can have blank lines and comments in the namelist input file\n"
            "! place these comments between NAMELISTs\n"
            "\n"
            "!\n"
            "! not every compiler supports comments within the namelist\n"
            "!	in particular vastf90/g77 does not\n"
            "!\n"
            "! some will skip NAMELISTs not directly referenced in read\n"
            "!&BOGUS rko=1 /\n"
            "!\n"
            "&TTDATA \n"
            " TTREAL =  1.,\n"
            " TTINTEGER = 2,\n"
            " TTCOMPLEX = (3.,4.), \n"
            " TTCHAR = 'namelist', \n"
            " TTBOOL = .TRUE./\n"
            "&AADATA\n"
            " AAREAL =  1.  1.  2.  3., \n"
            " AAINTEGER = 2 2 3 4, \n"
            " AACOMPLEX = (3.,4.) (3.,4.) (5.,6.) (7.,7.), \n"
            " AACHAR = 'namelist' 'namelist' 'array' ' the lot', \n"
            " AABOOL = .TRUE. .TRUE. .FALSE. .FALSE./\n"
            "&XXDATA \n"
            " XXREAL =  1., \n"
            " XXINTEGER = 2, \n"
            " XXCOMPLEX = (3.,4.)/")
        namelist_dict = namelist2dict(StringIO(groups))
        self.assertEqual(namelist_dict, {
            "TTDATA": [{
                "TTREAL":  1.0,
                "TTINTEGER": 2,
                "TTCOMPLEX": 3.0 + 4.0j,
                "TTCHAR": "namelist",
                "TTBOOL": True}],
            "AADATA": [{
                "AAREAL": [1.0, 1.0, 2.0, 3.0],
                "AAINTEGER": [2, 2, 3, 4],
                "AACOMPLEX": [3.0 + 4.0j, 3.0 + 4.0j, 5.0 + 6.0j, 7.0 + 7.0j],
                "AACHAR": ["namelist", "namelist", "array", " the lot"],
                "AABOOL": [True, True, False, False]}],
            "XXDATA": [{
                "XXREAL":  1.0,
                "XXINTEGER": 2,
                "XXCOMPLEX": 3.0 + 4.0j}]})


if __name__ == '__main__':
    unittest.main()