# coding: utf-8
# based on http://baguzin.ru/wp/?p=7873

import re


class AssParser:
    def __init__(self):
        self.dialog_re = re.compile(r'Dialogue:(?:[^,]*,){9}(.*)')

    def parse(self, file):
        result = []
        for line in file:
            text = self._get_text(line)
            if text:
                result.append(text)
        return result

    def _get_text(self, line):
        match = self.dialog_re.match(line)
        if match:
            text = self._strip_common_tags(match.group(1))
            if not self._has_tags(text):
                return text

    def _strip_common_tags(self, text):
        # http://docs.aegisub.org/3.2/ASS_Tags/
        text = text.replace(r'\n', ' ')
        text = text.replace(r'\N', ' ')
        text = text.replace(r'\h', ' ')
        text = re.sub(r'\\i[01]', '', text)
        text = re.sub(r'\\b[\d]+', '', text)
        text = re.sub(r'\\u[01]', '', text)
        text = re.sub(r'\\s[01]', '', text)
        text = re.sub(r'\\[xy]?bord[\d.]+', '', text)
        text = re.sub(r'\\[xy]?shad[\d.]+', '', text)
        text = re.sub(r'\\be[\d.]+', '', text)
        text = re.sub(r'\\blur[\d.]+', '', text)
        text = re.sub(r'\\fn[^\\()}]+', '', text)
        text = re.sub(r'\\fs[\d.]+', '', text)
        text = re.sub(r'\\fsc[xy][\d.]+', '', text)
        text = re.sub(r'\\fsp[\d.]+', '', text)
        text = re.sub(r'\\fe[\d]+', '', text)
        text = re.sub(r'\\[1234]?c&H[\daAbBcCdDeEfF]+&', '', text)
        text = re.sub(r'\\alpha&H[\daAbBcCdDeEfF]+', '', text)
        text = re.sub(r'\\[1234]a&H[\daAbBcCdDeEfF]+', '', text)
        text = re.sub(r'\\an?[\d]+', '', text)
        text = re.sub(r'\\q[\d]', '', text)
        text = re.sub(r'\\r(?:[^\\()}]+)?', '', text)
        text = text.replace(r'{}', '')
        return text

    def _has_tags(self, text):
        return '{\\' in text


class ReadabilityIndex:
    def __init__(self, sentences):
        self.words_re = re.compile(ur'[А-Яа-яЁё]+', re.UNICODE)
        self.vowels_re = re.compile(ur'[аоэиуыеёюяАОЭИУЫЕЁЮЯ]', re.UNICODE)
        self.words = 0.0
        self.complex_words = 0.0  # 4 or more syllables (for russian words)
        self.syllables = 0.0
        self.sentences = 0.0

        for sentence in sentences:
            self.sentences += 1
            for word in self._break_sentence(sentence):
                self.words += 1
                syllables_count = self._get_syllables_count(word)
                self.syllables += syllables_count
                if syllables_count > 3:
                    self.complex_words += 1

    def _break_sentence(self, sentence):
        return self.words_re.findall(sentence.decode('utf8'))

    def _get_syllables_count(self, word):
        vowels = self.vowels_re.findall(word)
        return max(1, len(vowels))

    def __repr__(self):
        return '\n'.join([
            #'flesch_index %.2f' % self.flesch_index(),
            'flesch_index_ru %.2f (bigger is better)' % self.flesch_index_ru(),
            #'flesch_kincaid_index %.2f' % self.flesch_kincaid_index(),
            #'gunning_fog_index %.2f' % self.gunning_fog_index(),
            'gunning_fog_index_ru %.2f (lower is better)' % self.gunning_fog_index_ru(),
        ])

    def flesch_index(self):
        asl = self.words / self.sentences
        asw = self.syllables / self.words
        return 206.835 - 1.015 * asl - 84.6 * asw

    def flesch_index_ru(self):
        asl = self.words / self.sentences
        asw = self.syllables / self.words
        return 206.835 - 1.3 * float(asl) - 60.1 * float(asw)

    def flesch_kincaid_index(self):
        asl = self.words / self.sentences
        asw = self.syllables / self.words
        return 0.39 * float(asl) + 11.8 * float(asw) - 15.59

    def gunning_fog_index(self):
        return 0.4 * (self.words / self.sentences + 100.0 * self.complex_words / self.words)

    def gunning_fog_index_ru(self):
        return 0.4 * (0.78 * self.words / self.sentences + 100.0 * self.complex_words / self.words)


if __name__ == '__main__':
    import os
    from glob import glob

    def escape_glob(path):
        transdict = {
                '[': '[[]',
                ']': '[]]',
                '*': '[*]',
                '?': '[?]',
                }
        rc = re.compile('|'.join(map(re.escape, transdict)))
        return rc.sub(lambda m: transdict[m.group(0)], path)

    def stat_dir(dirpath):
        print dirpath
        ass = AssParser()
        sentences = []
        for filepath in glob(os.path.join(escape_glob(dirpath), '*.ass')):
            with open(filepath, 'r') as f:
                sentences.extend(ass.parse(f))
        print ReadabilityIndex(sentences)
        print ''

    def stat_dirs(dirpath):
        for path in glob(os.path.join(escape_glob(dirpath), '*')):
            if os.path.isdir(path):
                stat_dir(path)

    stat_dirs(r'.\subs')
