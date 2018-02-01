import csv
import re
from os import listdir
from os.path import isfile, join


def main():
    folder = './logs'
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    log_files = filter(
        lambda f: re.findall('internet_log.*?\.csv', f), onlyfiles)
    print 'Found {} log files: {!r}'.format(len(log_files), log_files)
    internet_failures = []
    for filename in log_files:
        internet_failures.extend(search_pattern(
            join(folder, filename),
            'DHCPC Entering released state', 'Mensagem'))

    print 'Found {} internet problems'.format(len(internet_failures))
    print '====== INFO ======='
    for i in internet_failures:
        print i['Data']
    print '====== END ======='


def search_pattern(filename, pattern, field):
    fp = open(filename, 'r')
    results = []
    for data in csv.DictReader(fp):
        if re.findall(pattern, data[field]):
            results.append(data)

    return results

if __name__ == '__main__':
    main()
