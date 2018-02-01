import urllib2
import signal
import sys
import time
import locale
import xml.etree.ElementTree as ET

locale.setlocale(locale.LC_ALL, 'en_US')


def signal_handler(signal, frame):
    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    print 'GOVERNOR'
    print 'ISLAND WIDE RESULTS'
    print '\n---------'

    while True:
        xml_file = urllib2.urlopen('http://div1.ceepur.org/REYDI_NocheDelEvento/data/GOBERNADOR_ISLA.xml').read()

        obj = ET.fromstring(xml_file)

        print obj.find('date').text

        print '\n'

        candidates = obj.findall('option')

        winner = candidates[0]

        print u'%s' % winner.find('name').find('es').text
        print u'%s' % winner.find('pe').find('es').text

        winner_votes = int(winner.find('votes').text)
        loser_votes = int(candidates[1].find('votes').text)

        winning_by = locale.format('%d', (winner_votes - loser_votes), grouping=True)
        winner_votes = locale.format('%d', winner_votes, grouping=True)
        loser_votes = locale.format('%d', loser_votes, grouping=True)

        print 'Winning by: %s' % winning_by
        print '%s vs %s' % (winner_votes, loser_votes)

        print '\n---------\n'

        time.sleep(5)
