#!/usr/bin/env python
"""
A very simplistic script to check for pep8 errors in the lines of a file that
are to be committed. This is useful if you have files with lots of pep8 errors,
but you only want to know about the errors in the lines you have altered.
"""
import sys
import subprocess


def system(*args, **kwargs):
    stdin = kwargs.pop('input', None)
    kwargs.setdefault('stdin', subprocess.PIPE)
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate(input=stdin)
    return out


def git_diff():
    diff = system('git', 'diff', '--cached')
    return diff.strip().split("\n")


def pep8_output(file_list):
    errors = []
    prefix = len('stdin')

    for filename in file_list:
        # run the cached version of the file through pep8
        cached_file = system('git', 'show', ':' + filename)
        err = system('pep8', '-r', '-', input=cached_file)
        errors += [filename + e[prefix:] for e in err.strip().split("\n")]

    return errors


def parse_diff(lines):
    files = {}
    current_file = None
    counter = 0

    for line in lines:
        if line.startswith('-'):
            continue

        if line.startswith('+++'):
            # starting on a new file
            current_file = line[6:].strip()
            files[current_file] = []
            continue

        if line.startswith('diff'):
            # finished with this file
            current_file = None
            continue

        if current_file is None:
            # if we are not currently parsing a file, skip the line
            continue

        if line.startswith('@@'):
            # set new starting point
            counter = -1
            base_line = int(line.split()[2].split(',')[0])
            continue

        counter += 1

        if line.startswith('+'):
            files[current_file].append(base_line + counter)

    return files


def parse_pep8(lines):
    errors = []

    for line in lines:
        parts = line.split(':')
        errors.append((parts[0].strip(), int(parts[1]), line))

    return sorted(errors)


def main():
    # get list of changed files and lines
    diff = git_diff()
    changed_files = parse_diff(diff)

    # get list of pep8 errors for the changed files
    py_files = [f for f in changed_files.keys() if f.endswith('.py')]
    output = pep8_output(py_files)
    pep8_errors = parse_pep8(output)

    # check changed lines for errors
    errors = [err for filename, lineno, err in pep8_errors
              if lineno in changed_files[filename]]

    # if errors found, print them and exit with error code
    if errors:
        print "Aborting commit due to pep8 errors:"
        for err in errors:
            print err
        sys.exit(1)


if __name__ == '__main__':
    main()