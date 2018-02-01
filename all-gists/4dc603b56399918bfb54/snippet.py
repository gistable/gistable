import re
import csv
import urllib


class Parse:

    params = re.compile('(?P<key>[\S]*)=\{(?P<value>[\S]*)\}')
    prep = re.compile('(?P<key>[\S]*)=(?P<value>[\S]*)')

    def __init__(self, file):
        self.filename = file

    def run(self):
        params = []
        log = open(self.filename, 'r')
        line = log.readline()
        while line:
            res = self._parse_line(line)
            if res:
                params.append(self._encode_line(res))
            line = log.readline()
        self._save(params)
        log.close()

    def _parse_line(self, line):
        result = self.prep.findall(line)
        if result and '/solr' in result[0] and '/select' in result[1]:
            return self._parse_params(line)

    def _parse_params(self, line):
        result = self.params.search(line)
        if result is not None:
            regex = result.groups()
            if regex[0] == 'params':
                return regex[1]

    def _encode_line(self, line):
        return urllib.urlencode(dict([sand.split('=', 1) for sand in line.replace('+', ' ').replace('%25', '%').split('&')]))

    def _save(self, lines):
        with open(self.filename.replace('log', 'csv'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            for line in lines:
                writer.writerow([line])

parse = Parse('solr-main-2m.log')
parse.run()