#!/usr/bin/env python3
'''
Make sure to backup your anki database before trying this script. You will definitely need to update
the CARD_TYPES before running.
'''
import sqlite3
from hashlib import sha1
# from anki.utils import fieldChecksum
import re
import sys
import time
import requests
import json

ANKI_DATABASE_COPY = '/tmp/collection.anki2'
CARD_TYPES = ['put', 'card', 'types']  # put your card types here

stats = {
    'not_found': 0,
    'found': 0,
    'found_conjugated': 0,
    'existing_sound': 0,
    'no_kanji_or_kana': 0,
}
url = 'http://assets.languagepod101.com/dictionary/japanese/audiomp3.php'
unicode_regx = re.compile('[\x00-\x7F]')
word_sep_regx = re.compile('[\[\].,0-9a-zA-Z`\/「」、。：；０-９ー\s].')


def go(last_mod):
    conn = sqlite3.connect(ANKI_DATABASE_COPY)
    cur = conn.cursor()
    mod_time = int(time.time()) - last_mod
    cur.execute('SELECT models FROM col')
    models_str = cur.fetchall()[0][0]
    models = json.loads(models_str)
    note_mid_nums = []
    audio_field_indices = []
    cards = []
    for mid, card_type in models.items():
        if card_type['name'] in CARD_TYPES:
            for idx, field in enumerate(card_type['flds']):
                if field['name'] == 'Audio':
                    audio_field_idx = idx

            if audio_field_idx:
                audio_field_indices.append(idx)
                cur.execute('SELECT * FROM notes WHERE mid=? AND mod>?', (int(mid), mod_time))
                cards.append(cur.fetchall())

                print("Found %d %s type cards" % (len(cards[-1]), card_type['name'], ))

    for card_type_idx in range(0, len(cards)):
        for card in cards[card_type_idx]:
            fields = card[6].split('\x1f')
            id = card[0]
            kanji = find_word(fields[0])
            kana = find_word(fields[1])
            if kana == '':
                if kanji == '':
                    print("No kanji/kana for %s %s" % (fields[0], fields[1]))
                    stats['no_kanji_or_kana'] += 1
                    continue
                kana = kanji

            existing_sound = fields[audio_field_indices[card_type_idx]].strip()
            if existing_sound != '':
                # print("already has audio %s %s" % (kanji, kana))
                stats['existing_sound'] += 1
                continue

            conjugated = False
            try:
                r = requests.get(url, params={'kanji': kanji, 'kana': kana })
                if r.headers['Content-length'] == '52288':

                    # now try conjugating
                    attempts = to_dict_form(kanji, kana)
                    for attempt in attempts:
                        conjugated_kanji, conjugated_kana = attempt
                        r = requests.get(url, params={'kanji': conjugated_kanji, 'kana': conjugated_kana})
                        print("Trying %s %s for %s %s" % (conjugated_kanji, conjugated_kana, kanji, kana))
                        if r.headers['Content-length'] != '52288':
                            conjugated = True
                    if not conjugated:
                        print("NOT found %s %s" % (kanji, kana))
                        stats['not_found'] += 1
                        continue

                if conjugated:
                    print("Found conjugated form %s %s" % (kanji, kana))
                    stats['found_conjugated'] += 1
                else:
                    print("Found %s %s" % (kanji, kana))
                    stats['found'] += 1
                sound_file_name = '%s_%s.mp3' % (kanji, kana)
                sound_file_path = '/tmp/%s' % sound_file_name
                with open(sound_file_path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

                fields[audio_field_indices[card_type_idx]] = '[sound:%s]' % sound_file_name
                new_fields = str.join('\x1f', fields)
                mod = int(time.time())
                # need to set update sequence number (usn) to -1 to tell server we have updates
                cur.execute("UPDATE notes SET flds=?,mod=?,usn=? WHERE id=?", (new_fields, mod, -1, id))
            except Exception as e:
                print("Error with card %s" % e)

        # csum = fieldChecksum(new_fields[0])
    conn.commit()
    conn.close()

    print("Finished!\n\n%s" % stats)


def to_dict_form(kanji, kana):
    kana_root = kana[:-3]
    kanji_root = kanji[:-3]

    def _filled(poss):
        return [('%s%s' % (kanji_root, suff), '%s%s' % (kana_root, suff)) for suff in poss]

    if kanji[-3:] == 'します' and kana[-3:] == 'します':
        # group 3
        return _filled(['する', ''])
    elif kanji[-2:] == 'ます' and kana[-2:] == 'ます' :
        if kana[-3] in ('き', 'ぎ', 'み', 'り', 'い', 'し', 'ち',):
            # group 1
            if kana[-3] == 'き':
                return _filled(['く'])
            elif kana[-3] == 'ぎ':
                return _filled(['ぐ'])
            elif kana[-3] == 'み':
                return _filled(['む'])
            elif kana[-3] == 'り':
                return _filled(['る'])
            elif kana[-3] == 'い':
                return _filled(['う'])
            elif kana[-3] == 'し':
                return _filled(['す'])
            elif kana[-3] == 'ち':
                return _filled(['つ'])
        else:
            # group 2
            return [('%sる' % kanji[:-2], '%sる' % kana[:-2])]

    return []


def remove_non_unicode_characters(s):
    return unicode_regx.sub('', s)


def find_word(s):
    splitted = word_sep_regx.split(s.strip())
    for w in splitted:
        cleaned = remove_non_unicode_characters(w).strip()
        if cleaned != '':
            return cleaned
    return ''


if __name__ == '__main__':
    try:
        last_mod = int(sys.argv[1])
    except:
        last_mod = int(time.time())
    go(last_mod)
