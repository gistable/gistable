#!/usr/bin/env python
# encoding: utf-8

import re
from datetime import date
from path import path


class BackupPrune:

    name_pattern = re.compile(
        r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
        r'\.sql\.gz$'
    )

    keep_weekday = 6
    keep_daily = 7

    def __init__(self, backup_dir):
        self.backup_dir = path(backup_dir)
        self.today = date.today()

    def enumerate(self):
        for backup_path in sorted(self.backup_dir.listdir()):
            match = self.name_pattern.match(backup_path.name)
            if match:
                backup_date = date(
                    int(match.group('year')),
                    int(match.group('month')),
                    int(match.group('day')),
                )
                yield (backup_date, backup_path)

    def keep(self, backup_date):
        if backup_date.weekday() == self.keep_weekday:
            return True

        elif (self.today - backup_date).days < self.keep_daily:
            return True

        else:
            return False

    def test(self):
        for backup_date, backup_path in self.enumerate():
            if not self.keep(backup_date):
                print(u'✘', backup_path.name)
                backup_path.unlink()

def main():
    backup_dir = path(__file__).abspath().parent
    bp = BackupPrune(backup_dir)
    bp.test()


if __name__ == '__main__':
    main()
