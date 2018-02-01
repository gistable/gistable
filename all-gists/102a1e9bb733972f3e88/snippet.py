# -*- coding: utf-8 -*-
import pytest

def extract_matching_word(keep_words):
    if len(keep_words) == 0:
        return None

    words = map(lambda (k,v): (k, ''.join(v), len(v)), keep_words.iteritems())
    fullwords = filter(lambda v: v[0] == v[1], words)
    max_len = max(map(lambda v: v[2], fullwords))
    max_len_words = filter(lambda v: v[2] == max_len, fullwords)
    if len(max_len_words) > 0:
        da = map(lambda v: v[0], max_len_words)
        if len(da) > 0:
            return da[0]

    return None

def make_matching_words(morphemes_words, extract_dict):

    words = []
    keep = {}
    for w in morphemes_words:
        if len(keep) == 0:
            # マッチしていない場合、辞書から見つける
            keep = {k: [w] for k, v in extract_dict.iteritems() if extract_dict[k][0] == w}

        else:
            # マッチ済みから探す
            match = False
            for k in keep:
                if len(extract_dict[k]) > len(keep[k]) and extract_dict[k][len(keep[k])] == w:
                    # 合った
                    keep[k].append(w)
                    match = True

            if not match:
                # 今までの最高の単語数マッチ
                matching_word = extract_matching_word(keep)
                if matching_word:
                    words.append(matching_word)

                keep = {k: [w] for k, v in extract_dict.iteritems() if extract_dict[k][0] == w}

    matching_word = extract_matching_word(keep)
    if matching_word:
        words.append(matching_word)

    return words

class TestFunc(object):
    @pytest.mark.parametrize(("input", "expected"), [
        (['b'],                          []),
        (['b', 'a'],                     ['a']),
        (['b', 'a', 'd'],                ['a']),
        (['b', 'a', 'd', 'a'],           ['a', 'a']),
        (['b', 'a', 'd', 'a', 'b'],      ['a', 'ab']),
        (['b', 'a', 'd', 'a', 'b', 'c'], ['a', 'ab', 'c']),
    ])
    def test_make_matching_words(self, input, expected):
        extract_dict = {
            'c': ['c'],
            'a': ['a'],
            'ab': ['a', 'b'],
        }
        assert make_matching_words(input, extract_dict) == expected

if __name__ == '__main__':
    pytest.main()
