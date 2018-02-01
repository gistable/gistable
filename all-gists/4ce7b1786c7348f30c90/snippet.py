# -*- coding: utf8 -*-

#
# Graphite log simple parser.
# It parse functions and its arguments using python ast-tree.
#
# For each log line like:
# {
#   192.168.14.20  [23/Jul/2015:15:44:11 +0100]
#   "GET    /render?from=-4hours&noCache=True&hideLegend=False
#           &height=400&width=500&until=-&title=My%20Graphic
#           &target=cactiStyle(aliasByNode(foo.bar.baz))
#           &yMax=400&_uniq=bb9b7ee2db0c13e3 HTTP/1.1"
#   200 1074 "http://graphite.server.com/dashboard/"
#   "MyUserAgent" 0.048    0.048   "
# }
#
# It builds summary like:
# {
#   CASE = ["cactiStyle(aliasByNode('***', 1))"];
#       PARAMS = «{'from': ['-4hours'], 'until': ['-']}»;
#   <0> ~ CALL (0) = «aliasByNode('***', 1)»;
#   <0> ~ CALL (1) = «cactiStyle(aliasByNode('***', 1))»;
# }

from __future__ import absolute_import, division, print_function

import sys

import logging
import re
import ast
import urlparse

DEFAULT_LOG_NAME = './access.log'

METRICS_SYMBOL = '***'

WASTE_PARAM_LIST = [
    '_uniq',
    '_salt',
    'hideLegend',
    'drawNullAsZero',
    'noCache',
    'width',
    'height',
    'yMax',
    'yMin',
    'title',
]

WASTE_FUNC_LIST = [
    # 'alias',     # name
    # 'color',     # visual representation
    # 'dashed'     # visual representation
]


def main(argc, argv):
    """
        Open nginx log with graphite requests
        and prints it representation in terms of
        graphite-functions' calls and GET-parameters.
    """
    log_name = DEFAULT_LOG_NAME
    if argc > 1:
        log_name = argv[1]
    log_stream = open(log_name)
    while True:
        case_stack, param_dict = next(get_input_generator(log_stream), None)
        if not case_stack:
            break
        string = repr_case(case_stack, param_dict)
        print(string)


def repr_case(case_stack, param_dict):
    """
        Returns representation of a function call and GET-parameters
        for current log line. Also it returns representation of
        stack of arguments with functions' calls.

        :param case_stack: tuple(str, list)
            a call stack (with initial function call)
            for current log line (tuple(str, list))
        :param param_dict: dict
            a dictionary of GET-parameters (dict).
        :returns: str
            representation of current log line in terms of
            graphite-functions' calls and GET-parameters.
    """
    string = str()
    case_list = sorted([case for case, _ in case_stack])
    case_repr = "CASE = %s; PARAMS = «%s»;\n" % (case_list, param_dict)
    string += case_repr
    for case_num, (_, call_stack) in enumerate(list(case_stack)):
        for call_depth, call in enumerate(call_stack):
            call_repr = "<%s> ~ CALL (%s) = «%s»;\n" % (case_num, call_depth, call)
            string += call_repr
    return string


def get_input_generator(stream):
    """
        Returns generator for a function call, it's stack
        of functions arguments and GET-parameters for certain log line.

        :param stream: a file opened for read
            opened log file or stream
        :yields tuple(tuple(str, list), dict)
            *   a call stack (with initial function call)
                for current log line (tuple(str, list))
            *   and a dictionary of GET-parameters (dict).
    """
    for log_line in stream:
        if has_param(log_line):
            param_string = get_request_line(log_line)
            param_dict = get_param_dict(param_string)
            target_list, param_dict = get_target_list(param_dict)
            case_stack = handle_target_list(target_list)
            yield case_stack, param_dict


def has_param(line, param_marker='/render?'):
    """
        Check if it is normal graphite input in nginx.

        :param line: str
            line from nginx log.
        :param param_marker: str
            substring that should be a in line from nginx log.
        :returns: bool
            has parameters or not.
    """
    if param_marker in line:
        return True
    return False


def get_request_line(line, start_marker='/render?', stop_marker='HTTP/1.1'):
    """
        Singles out string of GET-parameters form nginx-line.

        :param line: string
            line from nginx log.
        :param start_marker: string
            substring of nginx-line after what string of parameters starts.
        :param stop_marker: string
            substring of nginx-line before what string of parameters starts.
        :returns: string
            string of GET-parameters.
    """
    _, _, rest = line.partition(start_marker)
    param_string, _, _ = rest.partition(stop_marker)
    return param_string


def get_param_dict(param_string):
    """
        Creates parameters dict from string of GET-parameters and filter it.

        :param param_string: string
            string of GET-parameters.
        :returns: dict
            dictionary of filtered GET-parameters.
    """
    param_dict = urlparse.parse_qs(param_string)
    filtered_param_dict = filter_param_dict(param_dict)
    return filtered_param_dict


def filter_param_dict(param_dict, waste_param_list=WASTE_PARAM_LIST):
    """
        Delete unnecessary parameters from target dictionary of GET-parameters.

        :param param_dict: dict
            dictionary of GET-parameters.
        :param waste_param_list: list
            list of parameters, that should be deleted from target dictionary.
        :returns: dict
            dictionary of filtered GET-parameters.
    """
    for bad_param in waste_param_list:
        if param_dict.get(bad_param):
            del param_dict[bad_param]
    return param_dict


def get_target_list(param_dict, target_key='target'):
    """
        Returns the list of parameters that contains graphite-formulas
        and metrics.

        :param param_dict: dict
            dictionary of GET-parameters.
        :param target_key: sting
            name of key with graphite-formulas and metrics.
        :returns: tuple(list, dict)
            tuple of:
                *   list of string with parameters that
                    contains graphite-formulas and metrics;
                *   dict of GET-parameters without formulas and metrics
    """
    target_list = param_dict.get(target_key, [])
    if target_list:
        param_dict.pop(target_key)
    return (target_list, param_dict)


def handle_target_list(target_list):
    """
        Handle each parameter with graphite-formulas and metrics.

        :param target_list: list
            list of parameters with graphite-formulas and metrics.
        :returns: tuple(tuple(str, list), …)
            a tuple of tuples as results of `handle_target`.
            Results of `handle_target`:
                * a initial function call aka «case of use» (str)
                * and a stack of functions' calls (list).
    """
    result = (handle_target(target) for target in target_list)
    return tuple(result)


def handle_target(target_string):
    """
        Parse target string and represent it as stack of function calls.

        :param target_string: str
            string with graphite-formulas and metrics.
        :returns: tuple(str, list)
            a tuple of:
                * a initial function call aka «case of use» (str)
                * and a stack of functions' calls (list).
    """
    escaped_target_string = escape_metrics(target_string)
    case, call_stack = explode(escaped_target_string)
    return (case, call_stack)


def escape_metrics(target_string):
    """
        Replace special symbols in target string.

        :param target_string: string
            one item parameter with graphite-formulas and metrics.
        :returns: string
            string where all special symbols replaced to `_`.
    """

    assert isinstance(target_string, str)
    target_string = re.sub(
        '[\*\-%\@\?\{\}\^\[\]\<\>]',
        '_',
        target_string
    )
    target_string = re.sub(
        '([a-zA-Z_]\w+)\.(\d)',
        '\g<1>_\g<2>',
        target_string
    )

    return target_string


def get_metrics_symbol(symbol=METRICS_SYMBOL):
    """
        Returns a symbol in which we change metrics' names.
        Wraps it in  quotes.

        :param symbol: str
            a symbol in what we change metrics' names.
        :returns: str
            quoted symbol in which we change metrics' names.
    """

    if isinstance(symbol, unicode):
        return u"'%s'" % (symbol)
    return "'%s'" % (symbol)


def explode(string):
    """
        Explodes escaped target string to a stack
        of strings with call of all functions.
        This stack respresented as a list.
        It works with `escaped_target_string` as python code,
        and builds python-ast tree for it.

        :param string: str
            escaped target string with graphite-formulas and metrics.
        :returns: tuple(str, list)
            A tuple of:
                * a initial function call (str)
                * and a stack of functions' calls (list).
    """

    parsed_ast = ast.parse(string)
    initial_call, call_stack = repr_ast(parsed_ast)
    return initial_call, call_stack


def repr_ast(tree):
    """
        Walks into python-ast tree and build a stack of functions' calls.

        :param tree: _ast.Module
            escaped target string with graphite-formulas and metrics.
        :returns: tuple(str, list)
            A tuple of:
                * a initial function call (str)
                * and a stack of functions' calls (list).
    """

    call_stack = []
    for expr in tree.body:
        initial_call, call_stack = repr_node(expr.value, call_stack)
    return initial_call, call_stack


def repr_node(node, call_stack):
    """
        Check type of current node of ast-tree
        and apply appropriate handler.
        It uses indirect recursion due to `repr_call`.

        :param node: ast.Node
            escaped target string with graphite-formulas and metrics.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a current node representation (str)
                * and a new stack state  (list).
    """
    if isinstance(node, ast.Call):
        return repr_call(node, call_stack)
    elif isinstance(node, ast.Num):
        return repr_num(node, call_stack)
    elif isinstance(node, ast.Str):
        return repr_str(node, call_stack)
    elif isinstance(node, ast.Attribute):
        return repr_attribute(node, call_stack)
    elif isinstance(node, ast.Name):
        return repr_name(node, call_stack)
    return "'unknown'", call_stack


def repr_call(call, call_stack):
    """
        Returns representation of current function call.
        It uses indirect recursion due to `repr_node`:
        applies `repr_node` for all arguments of call-node.
        Also it adds current function call to call_stack.

        :param call: ast.Call
            an ast-object of certain function call.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a representation of current function call (str)
                * and a new stack state (list).
    """
    func_name = call.func.id
    arg_list = call.args
    arg_repr = (repr_node(arg, call_stack)[0] for arg in arg_list)
    call_string = "%s(%s)" % (func_name, ', '.join(arg_repr))
    call_stack = add_to_stack(func_name, call_string, call_stack)
    return call_string, call_stack


def add_to_stack(func_name, call_string, call_stack, waste_func_list=WASTE_FUNC_LIST):
    """
        Adds current function call to call_stack
        if name of current function is not in the list of «waste» functions.

        :param func_name: str
            current function name.
        :param call_string: str
            a string representation of current function call.
        :param call_stack: list
            a stack of functions' calls.
        :param waste_func_list: list
            a list of excluded funtions' names
        :returns: list
            a new stack state (list).
    """
    if func_name not in waste_func_list:
        call_stack += [call_string]
    return call_stack


def repr_num(num, call_stack):
    """
        Returns representation of current number node.

        :param num: ast.Num
            a current number node.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a string representation of number node (str)
                * and a new stack state (list).
    """
    return str(num.n), call_stack


def repr_str(string, call_stack):
    """
        Returns quoted representation of current string node.

        :param num: ast.Str
            a current string node.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a string representation of string node (str)
                * and a new stack state (list).
    """
    return "'%s'" % string.s, call_stack


def repr_attribute(_, call_stack):
    """
        Returns a special symbol in which we change metrics' names.

        :param _: ast.Attribute
            a current attribute node.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a special «metrics'» symbol (str)
                * and a new stack state (list).
    """
    return get_metrics_symbol(), call_stack


def repr_name(_, call_stack):
    """
        Returns a special symbol in which we change metrics' names.

        :param _: ast.Name
            a current attribute node.
        :param call_stack: list
            a stack of functions' calls.
        :returns: tuple(str, list)
            A tuple of:
                * a special «metrics'» symbol (str)
                * and a new stack state (list).
    """
    return get_metrics_symbol(), call_stack


def debug(*args, **kwargs):
    """
        Wrappers logging for debug.
    """
    return logging.warn(*args, **kwargs)


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
