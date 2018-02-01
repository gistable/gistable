#!/usr/bin/env python
"""
Git commit hook:
 .git/hooks/commit-msg

 Check commit message according to angularjs guidelines:
  * https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit#
"""

import sys
import re

valid_commit_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', ]
commit_file = sys.argv[1]
help_address = 'https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit#'

with open(commit_file) as commit:
    lines = commit.readlines()
    if len(lines) == 0:
        sys.stderr.write("\nEmpty commit message\n")
        sys.stderr.write("\n - Refer commit guide: %s\n\n" % help_address)
        sys.exit(1)

    # first line
    line = lines[0]
    m = re.search('^(.*)\((.*)\): (.*)$', line)

    if not m or len(m.groups()) != 3:
        sys.stderr.write("\nFirst commit message line (header) does not follow format: type(scope): message\n")
        sys.stderr.write("\n - Refer commit guide: %s\n\n" % help_address)
        sys.exit(1)
    commit_type, commit_scope, commit_message = m.groups()
    if commit_type not in valid_commit_types:
        sys.stderr.write("\nCommit type not in valid ones: %s\n" % ", ".join(valid_commit_types))
        sys.stderr.write("\n - Refer commit guide: %s\n\n" % help_address)
        sys.exit(1)

    if len(lines) > 1 and lines[1].strip():
        sys.stderr.write("\nSecond commit message line must be empty\n")
        sys.stderr.write("\n - Refer commit guide: %s\n\n" % help_address)
        sys.exit(1)

    if len(lines) > 2 and not lines[2].strip():
        sys.stderr.write("\nThird commit message line (body) must not be empty\n")
        sys.stderr.write("\n - Refer commit guide: %s\n\n" % help_address)
        sys.exit(1)

sys.exit(0)