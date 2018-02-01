#!/usr/bin/env python
import argparse
import tempfile
import subprocess
import traceback


def u(somebytes):
    return None if somebytes is None else somebytes.decode('utf-8')


def run(cmd):
    cmd_args = cmd.split()
    print("$ {}".format(cmd))
    return u(subprocess.check_output(
        cmd_args,
        stderr=subprocess.STDOUT))


def mergein(branch, revno):
    print(run("bzr merge -c {} {}".format(revno, branch)))


def commit_msg(branch, revno):
    out = run("bzr log -r {} {}".format(revno, branch))
    print(out)
    msg = ""
    collect = False
    for line in out.splitlines():
        if not collect and line.startswith('message:'):
            collect = True
        elif collect and line.startswith('------'):
            collect = False
        elif collect:
            msg += line.lstrip() + "\n"
    return msg


def commit(msg):
    f = tempfile.NamedTemporaryFile(prefix="commit_msg", mode="w")
    f.write(msg)
    f.flush()
    print(run("bzr commit -F {}".format(f.name)))


def attach_procedence(msg, branch, revno):
    return msg + "\nFrom {} revno {}".format(branch, revno)


def cherrypick(branch, start, end):
    for revno in range(start, end + 1):
        print("Cherrypicking revno {} from {}".format(revno, branch))
        try:
            mergein(branch, revno)
            msg = commit_msg(branch, revno)
            msg = attach_procedence(msg, branch, revno)
            print("{} commit msg: {}".format(revno, msg))
            commit(msg)
        except Exception:
            traceback.print_exc()
            print("Cherrypicking stopped at revno {} from {}".format(
                revno, branch))
            return


def main():
    parser = argparse.ArgumentParser(description='Cherrypick bzr commits')
    parser.add_argument(
        'branch', type=str, help="Bazaar branch to pick commits from")
    parser.add_argument(
        'first', type=int, help="First revno to cherrypick")
    parser.add_argument(
        'last', type=int, nargs='?', help="Last revno to cherrypick")
    args = parser.parse_args()
    last = args.first if args.last is None else args.last
    cherrypick(args.branch, args.first, last)


if __name__ == "__main__":
    main()
