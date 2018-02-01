"""
Outputs history with bash and git aliases expanded.
"""
from __future__ import print_function

import re
from subprocess import check_output

BASH_ALIASES = {}
for line in check_output('bash -i -c "alias -p"', shell=True).split('\n'):
    if not line.strip():
        continue
    match = re.match(r"^alias (.+?)='(.+?)'\n*$", line)
    BASH_ALIASES[match.group(1)] = match.group(2)


GIT_ALIASES = {}
for line in check_output('git config --get-regexp alias*', shell=True).split('\n'):
    if not line.strip():
        continue

    match = re.match(r"^alias\.(.+?) (.+)$", line)
    GIT_ALIASES[match.group(1)] = match.group(2)


def expand(cmd):
    try:
        number, cmd = cmd.strip().split(' ', 1)
        cmd = cmd.strip()
    except ValueError:
        # empty line
        return cmd

    for alias, expansion in BASH_ALIASES.items():
        cmd = re.sub(r"^" + re.escape(alias) + '(\s|$)', expansion + ' ', cmd)
    for alias, expansion in GIT_ALIASES.items():
        cmd = re.sub(r"^git " + re.escape(alias) + "(\s|$)", "git %s " % expansion, cmd)

    return " %s  %s" % (number, cmd)


if __name__ == "__main__":
    for line in check_output('bash -i -c "history -r; history"', shell=True).split('\n'):
        print(expand(line))

