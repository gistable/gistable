import nltk

from nltk.tokenize.treebank import TreebankWordTokenizer

class TreebankSpanTokenizer(TreebankWordTokenizer):

    def __init__(self):
        self._word_tokenizer = TreebankWordTokenizer()

    def span_tokenize(self, text):
        ix = 0
        for word_token in self.tokenize(text):
            ix = text.find(word_token, ix)
            end = ix+len(word_token)
            yield (ix, end)
            ix = end

    def tokenize(self, text):
        return self._word_tokenizer.tokenize(text);
