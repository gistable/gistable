
#!/usr/bin/env python
# encoding: utf-8
"""
fingerprint_cluster.py
Based on http://code.google.com/p/google-refine/wiki/ClusteringInDepth
Created by Kyle Jensen on 2010-12-15.
"""

import re
NONALPHANUMSPACE_re = re.compile(r'[^\w\s]', re.I|re.UNICODE)

latin_to_uni = {
	'a' : (u'\u00C0',u'\u00C1',u'\u00C2',u'\u00C3',u'\u00C4',u'\u00C5',u'\u00E0',u'\u00E1',u'\u00E2',
		u'\u00E3',u'\u00E4',u'\u00E5',u'\u0100',u'\u0101',u'\u0102',u'\u0103',u'\u0104',u'\u0105',),
	'c' : (u'\u00C7',u'\u00E7',u'\u0106',u'\u0107',u'\u0108',u'\u0109',u'\u010A',u'\u010B',
	u'\u010C',u'\u010D',),
	'd' : (u'\u00D0',u'\u00F0',u'\u010E',u'\u010F',u'\u0110',u'\u0111',),
	'e' : (u'\u00C8',u'\u00C9',u'\u00CA',u'\u00CB',u'\u00E8',u'\u00E9',u'\u00EA',u'\u00EB',
	 u'\u0112',u'\u0113',u'\u0114',u'\u0115',u'\u0116',u'\u0117',u'\u0118',u'\u0119',u'\u011A',
	 u'\u011B',),
	'g' : (u'\u011C',u'\u011D',u'\u011E',u'\u011F',u'\u0120',u'\u0121',u'\u0122',u'\u0123',),
	'h' : (u'\u0124',u'\u0125',u'\u0126',u'\u0127',),
	'i' : (u'\u00CC',u'\u00CD',u'\u00CE',u'\u00CF',u'\u00EC',u'\u00ED',u'\u00EE',u'\u00EF',
	 u'\u0128',u'\u0129',u'\u012A',u'\u012B',u'\u012C',u'\u012D',u'\u012E',u'\u012F',u'\u0130',
	 u'\u0131',),
	'j' : (u'\u0134',u'\u0135',),
	'k' : (u'\u0136',u'\u0137',u'\u0138',),
	'l' : (u'\u0139',u'\u013A',u'\u013B',u'\u013C',u'\u013D',u'\u013E',u'\u013F',u'\u0140',
	 u'\u0141',u'\u0142',),
	'n' : (u'\u00D1',u'\u00F1',u'\u0143',u'\u0144',u'\u0145',u'\u0146',u'\u0147',u'\u0148',
	 u'\u0149',u'\u014A',u'\u014B',),
	'o' : (u'\u00D2',u'\u00D3',u'\u00D4',u'\u00D5',u'\u00D6',u'\u00D8',u'\u00F2',u'\u00F3',
	 u'\u00F4',u'\u00F5',u'\u00F6',u'\u00F8',u'\u014C',u'\u014D',u'\u014E',u'\u014F',u'\u0150',
	 u'\u0151',),
	'r' : (u'\u0154',u'\u0155',u'\u0156',u'\u0157',u'\u0158',u'\u0159',),
	's' : (u'\u015A',u'\u015B',u'\u015C',u'\u015D',u'\u015E',u'\u015F',u'\u0160',u'\u0161',
	 u'\u017F',),
	't' : (u'\u0162',u'\u0163',u'\u0164',u'\u0165',u'\u0166',u'\u0167',),
	'u' : (u'\u00D9',u'\u00DA',u'\u00DB',u'\u00DC',u'\u00F9',u'\u00FA',u'\u00FB',u'\u00FC',
	 u'\u0168',u'\u0169',u'\u016A',u'\u016B',u'\u016C',u'\u016D',u'\u016E',u'\u016F',u'\u0170',
	 u'\u0171',u'\u0172',u'\u0173',),
	'w' : (u'\u0174',u'\u0175',),
	'u' : (u'\u00DD',u'\u00FD',u'\u00FF',u'\u0176',u'\u0177',u'\u0178',),
	'z' : (u'\u0179',u'\u017A',u'\u017B',u'\u017C',u'\u017D',u'\u017E',),
}

uni_to_latin = dict([(u,l) for l,d in latin_to_uni.iteritems() for u in d])
def latinize(x):
    """Try to find the best latin character for any unicode characters in a string"""
    return ''.join(uni_to_latin.get(y,y) for y in x)

def fingerprint(s):
    """ The fingerprint fron Google Refine
        http://code.google.com/p/google-refine/wiki/ClusteringInDepth
    """
    f = s.strip()
    f = f.lower()
    f = NONALPHANUMSPACE_re.sub('', f)
    f = u' '.join(sorted(latinize(x) for x in set(f.split())))
    return f


def main():
    examples = [
        u'Comment ça va ? Très bien',
        u'woot hey Kyle JenseN ' + u'\u0179dd'
    ]
    for ex in examples:
        print(fingerprint(ex))


if __name__ == '__main__':
    main()
