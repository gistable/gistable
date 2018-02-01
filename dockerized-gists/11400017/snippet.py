#!/usr/bin/env python
import os
import os.path
import re
import shutil
import sys

# Help message
HELP = """Slugify

Rename a file to contain only lowercase letters, digits, -, _, and .

Usage: slugify [options] file

Options
    -c, --copy     Make a copy of source instead of renaming it.
    -f, --force    Overwrite existing file when renaming.
    -h, --help     Display this help.
    -p, --preview  Display the new filename for the slugified file.
    -s, --string   Output a slugifiged string instead of operating on a file.

"""

# Reg Ex pattern to match any non-slug-friendly character
PATTERN = re.compile("""[^0-9a-z\-\._]{1}""")


def slugify(str):
    """
    Return a version of the string containing only lowercase letters, digits,
    hyphens, underscores, and period.
    """
    str = str.strip().lower()
    str = PATTERN.sub("-", str)
    return str


def help():
    """Output the help message and exit."""
    print(HELP)
    exit()


if __name__ == "__main__":

    # Help. Display help if no arguments or if "-h" or "--help" is present.
    if len(sys.argv) == 0 or "-h" in sys.argv or "--help" in sys.argv:
        help()
        exit()

    # Read the last argument as the source.
    source = sys.argv[-1]

    # Defaults
    copy = False
    force = False
    preview = False
    string = False

    # Read other arguments.
    for arg in sys.argv[1:-1]:
        if arg in ["-c", "--copy"]:
            copy = True
        elif arg in ["-f", "--force"]:
            force = True
        elif arg in ["-p", "--preview"]:
            preview = True
        elif arg in ["-s", "--string"]:
            string = True
        else:
            print("Unrecognized option \"%s\"" % arg)
            exit(1)

    # String mode. Output the slugified version of the source only.
    if string:
        print(slugify(source))
        exit()

    # Check if the source file exists.
    if os.path.exists(source):

        # Determine the slugified name for the file by converting only the
        # filename portion of the path.
        source_directory, source_basename = os.path.split(source)
        target_basename = slugify(source_basename)
        target = os.path.join(source_directory, target_basename)

        # Check if already slug friendly.
        if source == target:
            print("File \"%s\" is already slug-friendly." % source)
            exit()

        # Preview. Only show what the script would rename to and if that name
        # is already taken.
        if preview:
            print(target)
            if os.path.exists(target):
                print("WARNING. File with the slugified name already exists.")
                print("Use -f or --force option to overwrite.")
            exit()

        # Copy. Copy the file and exit.
        if copy:
            shutil.copyfile(source, target)
            exit()

        # Check if this new name is in use.
        if os.path.exists(target):
            if force:
                os.remove(target)
            else:
                print("File \"%s\" already exists." %target)
                exit(1)

        # Rename the file.
        os.rename(source, target)

    # Source does not match a file. Exit with error.
    else:
        print("File \"%s\" not found." %source)
        exit(1)
