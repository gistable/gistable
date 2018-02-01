
from gensim.models import Phrases
import sys

assert len(sys.argv) > 2, "Need gensim model path and output filename!"
in_path, out_path = sys.argv[:2]

class PrefixTree(object):
    def __init__(self, words, impl=dict, suffix_impl=list):
        self.word = words[0]
        self._suffix_impl = suffix_impl
        self.suffixes = impl()
        if len(words) > 1:
            self.add_suffixes(words[1:])

    @staticmethod
    def from_sentences(sentences):
        tree = PrefixTree([None])
        for sentence in sentences:
            tree.add_suffixes(sentence)
        return tree

    def add_suffix(self, word):
        self.add_suffixes([word])

    def add_suffixes(self, words):
        assert len(words) > 0, "Got suffixes with len < 1"
        if isinstance(self.suffixes, dict):
            if words[0] in self.suffixes:
                self.suffixes[words[0]].add_suffixes(words[1:])
            else:
                self.suffixes[words[0]] = PrefixTree(words, impl=self._suffix_impl)
        else:
            added = False
            for suffix in self.suffixes:
                if words[0] == suffix:
                    if len(words) > 1:
                        suffix.add_suffixes(words[1:])
                        added = True
            if not added:
                self.suffixes.append(PrefixTree(words))
                    

    def __getitem__(self, word):
        if isinstance(self.suffixes, dict):
            return self.suffixes[word]
        else:
            for suffix in self.suffixes:
                if suffix == word:
                    return suffix
        return None

    def __eq__(self, other):
        if isinstance(other, str):
            return self.word == other
        else:
            return self.word == other.word

    def _get_phrases(self, words):
        phrases = []
        rest = words
        while len(rest) > 0:
            phrase, rest = self._add_suffixes([], rest, self)
            if len(phrase) > 1:
                phrases.append(phrase)
            if len(phrase) == 0:
                rest = rest[1:]
        return phrases

    @classmethod
    def _add_suffixes(cls, so_far, words, root):
        if len(words) < 1:
            return so_far, words
        if words[0] not in root.suffixes:
            return so_far, words
        return cls._add_suffixes(so_far + words[:1], words[1:], root[words[0]])

    def export_phrases(self, sentences):
        for sentence in sentences:
            assert isinstance(sentence, list) 
            yield from self._get_phrases(sentence)

    def __hash__(self):
        return hash(self.word)

    def __len__(self):
        return len(self.suffixes) + sum(map(len, self.suffixes))

    def __repr__(self):
        branches = str(list(self.suffixes)[:10])
        if len(self.suffixes) > 10:
            branches = branches[:-1] + ', ...]'
        return 'PrefixTree with root {} and some branches {} of length {}'.format(self.word, branches, len(self))

    @staticmethod
    def load(path, indent='\t'):
        with open(path) as infile:
            root = PrefixTree([None])
            num_indents = 0
            phrase = []
            for idx, line in enumerate(infile):
                indents = line.strip('\n').split(indent)
                if len(indents) - num_indents > 1:
                    raise Exception("Found {} indents on line {}, expected at most {}".format(
                        len(indents), idx, num_indents + 1))
                elif len(indents) - num_indents == 1:
                    phrase.append(indents[-1])
                    num_indents = len(indents)
                elif len(indents) == num_indents:
                    if len(phrase) > 1:
                        root.add_suffixes(phrase)
                    phrase = phrase[:-1] + [indents[-1]]
                    num_indents = len(indents)
                else:
                    # Fewer indents
                    root.add_suffixes(phrase)
                    num_indents = len(indents)
                    phrase = phrase[:num_indents-1] + [indents[-1]]
            if len(phrase) > 1:
                root.add_suffixes(phrase)
        return root

    def export(self, whitespace='\t'):
        if self.word is None:
            base = ''
        else:
            base = whitespace
            yield self.word + '\n'

        if isinstance(self.suffixes, dict):
            suffixes = self.suffixes.values()
        else:
            suffixes = self.suffixes
        for suffix in suffixes:
            for line in suffix.export(whitespace):
                yield base + line.strip('\n') + '\n'

    def export_to_file(self, path):
        with open(path, 'w') as outfile:
            outfile.writelines(phrase_model_to_prefix_tree(model).export())


def is_phrase(m, *words):
    for i in range(len(words)):
        try:
            words[i] = words[i].encode()
        except:
            pass
    product = 1
    for word in map(str.encode, words):
        if word in m.vocab:
            product *= m.vocab[word]
        else:
            product = 0
            break
    if product == 0:
        return False
    score = (m.vocab[m.delimiter.join(map(str.encode, words))] - m.min_count) * len(m.vocab) / product
    return score > m.threshold


def make_phrase_filter(m):
    def filterer(phrase):
        return is_phrase(m, *phrase)
    return filterer


def phrase_candidates(m):
    for candidate in m.vocab:
        if m.delimiter in candidate:
            candidates = candidate.split(m.delimiter)
            for i in range(len(candidates)):
                try:
                    candidates[i] = candidates[i].decode()
                except:
                    pass
            yield candidates


def phrase_model_to_prefix_tree(model):
    candidates = phrase_candidates(model)
    return PrefixTree.from_sentences(filter(make_phrase_filter(model), candidates))


if __name__ == '__main__':
    model = Phrases.load(in_path)
    pretree = phrase_model_to_prefix_tree(model)
    pretree.export_to_file(out_path)
