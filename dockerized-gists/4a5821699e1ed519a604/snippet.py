# coding=utf-8
''' Guess at ISO-3166-2 admin 1 codes for Natural Earth data.

Uses subdivision names from Ola Holmström’s iso-3166-2:
    https://github.com/olahol/iso-3166-2.js/blob/master/data.csv

ne_10m_admin_1_states_provinces.csv is a direct CSV
export of Natural Earth admin-1 data as of Nov 8, 2012:
    https://github.com/nvkelso/natural-earth-vector/tree/c97860331/10m_cultural

Generates out.csv, which can be joined back to Natural Earth on adm1_code.
'''
from unicodecsv import reader, DictReader, writer
from unidecode import unidecode
from operator import itemgetter
from itertools import groupby
from fuzzywuzzy import fuzz
from re import split

def unidecode_lower(string):
    return unidecode(string).lower()

with open('olahol-iso-3166-2.csv') as file:
    iso_3166_2_rows = list()

    for row in reader(file):
        # Afghanistan,AF-BDS,Badakhshān,Province,Badaẖšan,AF-BDS*,12267,2,AF,AFG
        country, iso_3166_2, name, _, name_variants, _, _, _, iso_a2, _ = row
        
        names = split(r'(?: \[|\])', name) + name_variants.split(', ')
        names = set(map(unidecode_lower, filter(None, names)))

        iso_3166_2_rows.append(dict(country=country, iso_3166_2=iso_3166_2,
                                    name=name, name_variants=name_variants,
                                    iso_a2=iso_a2, names=names))

with open('ne_10m_admin_1_states_provinces.csv') as file:
    ne_admin1_rows = list()
    iso_3166_1s = set()

    for row in DictReader(file):
        # adm1_code,iso_a2,iso_3166_2,name,name_alt,name_local

        names = [row['name'], row['name_local']] + row['name_alt'].split('|')
        row['names'] = set(map(unidecode_lower, filter(None, names)))

        ne_admin1_rows.append(row)
        iso_3166_1s.add(row['iso_a2'])

for iso_a2 in iso_3166_1s:
    #if iso_a2 not in ('CM', 'RU', 'PL'): continue
    
    # Pick out the Natural Earth entries for this country only missing an ISO-3166-2 code.
    _ne_admin1_rows = [R for R in ne_admin1_rows if R['iso_a2'] == iso_a2 and R['iso_3166_2'].endswith('-')]
    _iso_3166_2_rows = [R for R in iso_3166_2_rows if R['iso_a2'] == iso_a2]
    
    print iso_a2

    #
    # Start with a high minimum cutoff, and work downwards
    # so that exact matches are found as early as possible.
    #
    for minimum_ratio in range(100, 79, -5):
        for ne_admin1_row in _ne_admin1_rows:
            best_ratio, best_iso_row = minimum_ratio, None
        
            for iso_3166_2_row in _iso_3166_2_rows:
                for ne_name in ne_admin1_row['names']:
                    for iso_name in iso_3166_2_row['names']:
                        ratio = fuzz.ratio(ne_name, iso_name)
                    
                        if ratio > best_ratio:
                            best_ratio, best_iso_row = ratio, iso_3166_2_row
        
            if best_iso_row:
                print best_ratio, ne_admin1_row['names'], best_iso_row['names'], best_iso_row['iso_3166_2']
                ne_admin1_row['iso_3166_2'] = best_iso_row['iso_3166_2']

                _iso_3166_2_rows.remove(best_iso_row)
                _ne_admin1_rows.remove(ne_admin1_row)

with open('out.csv', 'w') as file:
    cols = 'adm1_code,iso_a2,iso_3166_2,name,name_alt,name_local'.split(',')

    out = writer(file)
    out.writerow(cols)
    
    for row in ne_admin1_rows:
        out.writerow([row[col] for col in cols])
