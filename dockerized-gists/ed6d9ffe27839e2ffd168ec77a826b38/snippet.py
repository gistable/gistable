#! /usr/bin/python
import subprocess
import argparse


def sub_factory(parser, funcs):
    sub = parser.add_subparsers()
    for name, func in funcs:
        subp = sub.add_parser(name)
        subp.add_argument('issue', type=int, help='issue number')
        subp.set_defaults(func=func)


def find_branch(issue):
    for x in subprocess.check_output(['git', 'branch']).split('\n'):
        x = x.strip().replace('* ', '')
        if x.startswith('#{}_'.format(issue)):
            return x.decode('utf-8')


def g_push(branch):
    subprocess.check_output(['git', 'push', 'origin', branch])


def g_checkout(branch):
    subprocess.check_output(['git', 'checkout', branch])


def g_delbr(branch):
    subprocess.check_output(['git', 'branch', '-D', branch])


def g_merge(branch):
    subprocess.check_output(['git', 'merge', 'origin/' + branch])


if __name__ == '__main__':
    L = [(n.replace('g_', ''), f) for n, f in globals().items() if n.startswith('g_')]
    parser = argparse.ArgumentParser(description='git command aliases.')
    sub_factory(parser, L)

    args = parser.parse_args()
    branch = find_branch(args.issue)
    args.func(branch)