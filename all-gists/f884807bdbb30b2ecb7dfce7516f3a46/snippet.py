#!/usr/bin/env python
import subprocess


def get_tests_from_paste_buffer():
    return subprocess.check_output('pbpaste')


def run():
    raw_tests = get_tests_from_paste_buffer()
    tests = []
    for test in raw_tests.splitlines():
        test = test.strip()
        if not test:
            continue
        if test.endswith('.txt'):
            test = test.split('/')[-1]
            tests.append(test)
        elif ' (' in test:
            test = test.replace(' (', '\\s.*').replace(')', '')
            tests.append(test)
    print '|'.join(tests)


if __name__ == '__main__':
    run()
