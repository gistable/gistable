import sys

if sys.version_info.major != 3 or sys.version_info.minor < 3:
    print("This module requires Python version 3.3 or later")
    sys.exit(1)

import argparse
import inspect

class Argumentor:
    def __init__(self, description=None):
        self._parser = argparse.ArgumentParser(description=description)
        self._subparsers = self._parser.add_subparsers()

    def add(self, func):
        subparser = self._subparsers.add_parser(func.__name__, help=func.__doc__)
        subparser.set_defaults(_func=func)
        func_signature = inspect.signature(func)
        for name, arg in func_signature.parameters.items():
            if arg.kind != arg.POSITIONAL_OR_KEYWORD:
                continue
            arg_help = arg.annotation if arg.annotation is not arg.empty else None
            if arg.default is arg.empty:
                # a positional argument
                subparser.add_argument(name, help=arg_help)
            else:
                # an optional argument
                subparser.add_argument("-" + name[0], "--" + name,
                        help=arg_help,
                        action="store" if arg.default is None else "store_const",
                        const=arg.default)
        return func

    def parse(self):
        args = vars(self._parser.parse_args())
        func = args.pop("_func", self._parser.print_usage)
        func(**args)

if __name__ == "__main__":
    parser = Argumentor("An Argumentor Example")

    @parser.add
    def show(some_command: "some kind of command", option: "an option" = None):
        "show something"
        print("some_command:", some_command)
        print("option:", option)

    @parser.add
    def do(whatever: "something completely different", const_option: "eat spam" = "spam"):
        "do something"
        print("whatever:", whatever)
        print("const_option:", const_option)


    parser.parse()