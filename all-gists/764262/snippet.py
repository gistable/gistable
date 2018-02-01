"""
PWMSearch

Searches through a fasta sequence for the relevant Position Weight Matrices 
from the Jaspar Database.

"""
from __future__ import division

from optparse import OptionParser
from itertools import groupby, izip, count, imap, islice
import re, csv
import MOODS
from collections import defaultdict



def isheader(line):
    return line.startswith('>')

def PWMIter(handle):
    """Yields name/PWM"""
    num_re = re.compile('\d{1,}')
    line_gen = imap(lambda x: x.strip(), handle)
    name = None
    out = None
    for header, lines in groupby(line_gen, isheader):
        if header:
            name = lines.next()[1:]
        else:
            out = []
            for line in lines:
                out.append(map(int, num_re.findall(line)))

            yield name, out

def transpose(input):
    """transposes a list-of-lists"""

    return map(None, *input)

def ParseHeader(header):
    """Parses the structured header to retrieve relevant info"""

    parts = header.split('_')
    odict = {}
    odict['CHROM'] = parts[1]
    odict['START'] = int(parts[2])
    odict['STRAND'] = parts[4]
    return odict


def ProcessSeqs(SEQ_HANDLE, PWMS, THRESHOLD, WANT_REV = False, bg = None):
    """Yields matches on sequences in an 'interval' formatted dictionary"""

    pwm_names = map(lambda x: x[0], PWMS)
    pwm_mats = map(lambda x: x[1], PWMS)
    thresh = map(lambda x:MOODS.threshold_from_p(x, bg, THRESHOLD), pwm_mats)

    for interval in ReadInterval(SEQ_HANDLE):
        print interval['NAME']

        results = MOODS.search(interval['SEQ'].upper(), pwm_mats, thresh,
                               both_strands = WANT_REV, algorithm = 'lf',
                               absolute_threshold = True, bg = bg)

        for res, pwm_name, pwm_mat, th in zip(results, pwm_names, pwm_mats, thresh):
            width = len(pwm_mat[0])
            for position, score in res:
                if score > th:
                    yield {
                        'NAME':interval['NAME'],
                        'START':int(interval['START'])+position,
                        'END':int(interval['START'])+width+position,
                        'STRAND':interval['STRAND'],
                        'PWM':pwm_name,
                        'SCORE':score,
                        'CHROM':interval['CHROM'],
                        'SEQ':interval['SEQ'][position:(position+width)].upper()
                    }
                else:
                    print 'got bad result'

def ReadInterval(handle):
    """Reads an Interval file and returns a list of dicts for each row"""

    headers = ('CHROM', 'START', 'END', 'NAME', 'junk', 'STRAND',
               'junk7', 'junk8', 'junk9', 'junk10', 'junk11',
               'junk12', 'SEQ')

    for row in csv.DictReader(handle, fieldnames = headers,
                              delimiter = '\t'):
        yield row


def GetBG(handle):

    d = defaultdict(int)
    for row in islice(ReadInterval(handle), 10):
        for r in row['SEQ'].upper():
            d[r] += 1
    s = sum(d.values())

    return [d['A']/s, d['C']/s, d['G']/s, d['T']/s]


if __name__ == '__main__':

    parser = OptionParser()

    (options, args) = parser.parse_args()

    seqintervalfile = args[0]
    jasparfile = args[1]
    threshold = args[2]
    output_file = args[3]

    print 'Getting Background'
    with open(jasparfile) as handle:
        PWMS = list(PWMIter(handle))

    with open(seqintervalfile) as handle:
        bg = GetBG(handle)

    fields = ('CHROM', 'START', 'END', 'STRAND', 'NAME', 'PWM', 'SCORE', 'SEQ')
    with open(output_file, 'w') as handle:
        handle.write('#'+'\t'.join(fields) + '\n')
        with open(seqintervalfile) as f_handle:
            writer = csv.DictWriter(handle, fields, )
            for row in ProcessSeqs(f_handle, PWMS, float(threshold), bg = bg):
                writer.writerow(row)






