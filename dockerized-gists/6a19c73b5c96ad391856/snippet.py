#!/usr/bin/env python
import argparse
import sys
from subprocess import call, check_output

# version check
if sys.hexversion < 0x02070000:
    sys.exit('Python 2.7 or newer is required to run this program.')


def create_arg_parser():
    parser = argparse.ArgumentParser(prog='apk.py', 
        description='Various APK operations on a connected device.', 
        epilog='NOTE: Will only work if adb is on the system path and a device is connected.')
    subparsers = parser.add_subparsers(help='Available actions')

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='List all the packages on the device')
    parser_list.set_defaults(func=adb_list)

    # create the parser for the "path" command
    parser_path = subparsers.add_parser('path', help='List the APK path for the packages')
    parser_path.add_argument('package', nargs='+', help='The package name to get paths for')
    parser_path.set_defaults(func=adb_path)

    # create the parser for the "pull" command
    parser_pull = subparsers.add_parser('pull', help='Pull the APK matching the package')
    parser_pull.add_argument('package', nargs='+', help='The package name to pull from device')
    parser_pull.set_defaults(func=adb_pull)

    return parser


def adb_list(args):
    call(['adb', 'shell', 'pm', 'list', 'packages'])


def adb_path(args, output=True):
    adb_pkg_output_prefix = 'package:'  # NOTE: Google may change the adb cmd output (but unlikely)...
    paths = {}  # a dict of paths with the package as key
    for p in args.package:
        # get the APK path for package
        cmd_out = check_output(['adb', 'shell', 'pm', 'path', p])
        cmd_str = cmd_out.decode('UTF-8').strip()  # convert the bytes to str
        # only add to the results dict if it's the expected str format
        if cmd_str and cmd_str.startswith(adb_pkg_output_prefix):
            paths[p] = cmd_str[len(adb_pkg_output_prefix):]
            # print the path to the apk?
            if output:
                print(cmd_str)

    return paths


def adb_pull(args):
    paths = adb_path(args, False)
    for key in paths:
        call(['adb', 'pull', paths[key], '{0}.apk'.format(key)])


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    if len(sys.argv) > 1:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
