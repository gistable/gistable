"""
Uso: 

    with open('amostra.txt') as amostra:
        decode = make_decoder(amostra)
        
    with open('amostra.txt') as dados:
        for linha in dados:
            print decode(linha)
"""

from chardet.universaldetector import UniversalDetector


def make_decoder(data):
    detector = UniversalDetector()

    for line in data:
        detector.feed(line)
        if detector.done:
            break

    detector.close()
    apparent_encoding = detector.result.get('encoding')

    def decode(bstring):
        return bstring.decode(apparent_encoding)

    return decode

