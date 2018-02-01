#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The Snowball stemmer.
Pavel Perestoronin © 2013
"""

import re
import unittest


class Stemmer:
    # Helper regex strings.
    _vowel = "[аеиоуыэюя]"
    _non_vowel = "[^аеиоуыэюя]"

    # Word regions.
    _re_rv = re.compile(_vowel)
    _re_r1 = re.compile(_vowel + _non_vowel)

    # Endings.
    _re_perfective_gerund = re.compile(
        r"(((?P<ignore>[ая])(в|вши|вшись))|(ив|ивши|ившись|ыв|ывши|ывшись))$"
    )
    _re_adjective = re.compile(
        r"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|"
        r"ую|юю|ая|яя|ою|ею)$"
    )
    _re_participle = re.compile(
        r"(((?P<ignore>[ая])(ем|нн|вш|ющ|щ))|(ивш|ывш|ующ))$"
    )
    _re_reflexive = re.compile(
        r"(ся|сь)$"
    )
    _re_verb = re.compile(
        r"(((?P<ignore>[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|"
        r"нно))|(ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|"
        r"ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю))$"
    )
    _re_noun = re.compile(
        r"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|"
        r"ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$"
    )
    _re_superlative = re.compile(
        r"(ейш|ейше)$"
    )
    _re_derivational = re.compile(
        r"(ост|ость)$"
    )
    _re_i = re.compile(
        r"и$"
    )
    _re_nn = re.compile(
        r"((?<=н)н)$"
    )
    _re_ = re.compile(
        r"ь$"
    )

    def stem(self, word):
        """
        Gets the stem.
        """

        rv_pos, r2_pos = self._find_rv(word), self._find_r2(word)
        word = self._step_1(word, rv_pos)
        word = self._step_2(word, rv_pos)
        word = self._step_3(word, r2_pos)
        word = self._step_4(word, rv_pos)
        return word

    def _find_rv(self, word):
        """
        Searches for the RV region.
        """

        rv_match = self._re_rv.search(word)
        if not rv_match:
            return len(word)
        return rv_match.end()

    def _find_r2(self, word):
        """
        Searches for the R2 region.
        """

        r1_match = self._re_r1.search(word)
        if not r1_match:
            return len(word)
        r2_match = self._re_r1.search(word, r1_match.end())
        if not r2_match:
            return len(word)
        return r2_match.end()

    def _cut(self, word, ending, pos):
        """
        Tries to cut the specified ending after the specified position.
        """

        match = ending.search(word, pos)
        if match:
            try:
                ignore = match.group("ignore") or ""
            except IndexError:
                # No ignored characters in pattern.
                return True, word[:match.start()]
            else:
                # Do not cut ignored part.
                return True, word[:match.start() + len(ignore)]
        else:
            return False, word

    def _step_1(self, word, rv_pos):
        match, word = self._cut(word, self._re_perfective_gerund, rv_pos)
        if match:
            return word
        _, word = self._cut(word, self._re_reflexive, rv_pos)
        match, word = self._cut(word, self._re_adjective, rv_pos)
        if match:
            _, word = self._cut(word, self._re_participle, rv_pos)
            return word
        match, word = self._cut(word, self._re_verb, rv_pos)
        if match:
            return word
        _, word = self._cut(word, self._re_noun, rv_pos)
        return word

    def _step_2(self, word, rv_pos):
        _, word = self._cut(word, self._re_i, rv_pos)
        return word

    def _step_3(self, word, r2_pos):
        _, word = self._cut(word, self._re_derivational, r2_pos)
        return word

    def _step_4(self, word, rv_pos):
        _, word = self._cut(word, self._re_superlative, rv_pos)
        match, word = self._cut(word, self._re_nn, rv_pos)
        if not match:
            _, word = self._cut(word, self._re_, rv_pos)
        return word


class TestStemmer(unittest.TestCase):
    """
    Tests the stemmer.
    """

    _stemmer = Stemmer()

    def test_re_perfective_gerund_av(self):
        self.assertEqual(
            "ав",
            self._stemmer._re_perfective_gerund.search("слушав").group(),
        )

    def test_re_perfective_gerund_avshi(self):
        self.assertEqual(
            "авши",
            self._stemmer._re_perfective_gerund.search("сделавши").group(),
        )

    def test_re_perfective_gerund_avshis(self):
        self.assertEqual(
            "авшись",
            self._stemmer._re_perfective_gerund.search("испугавшись").group(),
        )

    def test_re_perfective_gerund_ivshis(self):
        self.assertEqual(
            "ившись",
            self._stemmer._re_perfective_gerund.search("нагуглившись").group(),
        )

    def test_re_adjective_emu(self):
        self.assertEqual(
            "ему",
            self._stemmer._re_adjective.search("читавшему").group(),
        )

    def test_re_participle_aem(self):
        self.assertEqual(
            "аем",
            self._stemmer._re_participle.search("воспринимаем").group(),
        )

    def test_re_participle_yvsh(self):
        self.assertEqual(
            "ывш",
            self._stemmer._re_participle.search("забывш").group(),
        )

    def test_re_reflexive_s(self):
        self.assertEqual(
            "сь",
            self._stemmer._re_reflexive.search("забывшись").group(),
        )

    def test_re_verb_aete(self):
        self.assertEqual(
            "аете",
            self._stemmer._re_verb.search("делаете").group(),
        )

    def test_re_verb_yla(self):
        self.assertEqual(
            "ыла",
            self._stemmer._re_verb.search("плыла").group(),
        )

    def test_re_noun_iiam(self):
        self.assertEqual(
            "иям",
            self._stemmer._re_noun.search("понятиям").group(),
        )

    def test_re_superlative_eishe(self):
        self.assertEqual(
            "ейше",
            self._stemmer._re_superlative.search("красивейше").group(),
        )

    def test_re_derivational_ost(self):
        self.assertEqual(
            "ость",
            self._stemmer._re_derivational.search("честность").group(),
        )

    def test_stem(self):
        """
        Uses http://snowball.tartarus.org/algorithms/russian/diffs.txt
        to test the stemmer.
        """

        with open("diffs.txt", "rt", encoding="utf-8") as diffs_file:
            diffs = diffs_file.readlines()
        for i, line in enumerate(diffs):
            word, stem = line.split()
            self.assertEqual(
                stem,
                self._stemmer.stem(word),
                "Diff in word: %s (%d/%d)" % (word, i + 1, len(diffs)),
            )


if __name__ == "__main__":
    unittest.main()
