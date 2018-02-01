#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import MeCab

class Word(object):
    
    def __init__(self,surface,feature):
        self.surface = surface
        self.feature = feature
    
    def is_connected(self):
        allowed_feature = [
            u"名詞,一般",
            u"名詞,数",
            u"名詞,サ変接続",
            u"名詞,接尾,一般",
            u"名詞,接尾,サ変接続",
            u"名詞,固有名詞",
            u"名詞,形容動詞語幹",
            u"記号,アルファベット",
        ]
        disallowed_symbols = set(map(lambda x:x, u"()[]<>|\"';,"))
        for rule in allowed_feature:
            if self.feature.startswith(rule) and \
                    self.surface not in disallowed_symbols:
                return True
        else:
            return False

    def is_adjective_stem(self):
        allowed_feature = [
            u"名詞,形容動詞語幹",
            u"名詞,ナイ形容詞語幹",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

    def is_prefix(self):
        allowed_feature = [
            u"接頭詞,名詞接続",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

    def is_postfix(self):
        allowed_feature = [
            u"名詞,接尾,形容動詞語幹",
            u"名詞,接尾,一般",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

    def is_digit_prefix(self):
        allowed_feature = [
            u"接頭詞,数接続",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

    def is_numerative(self):
        allowed_feature = [
            u"名詞,接尾,助数詞",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

    def is_digit(self):
        allowed_feature = [
            u"名詞,数",
        ]
        for rule in allowed_feature:
            if self.feature.startswith(rule):
                return True
        else:
            return False

def is_symbol_only(word):
    regexp = \
    re.compile(r'^[!"#\$\%\&\'\(\)\*\+,\-\./:;\<\=\>\?\@\[\\\]\^\_\`\{\}\~\|]+$')
    if regexp.search(word) != None:
        return True
    else:
        return False

def extract_noun(text):
    worddic = {}
    result = []
    c = MeCab.Tagger()
    res = c.parseToNode(text.encode("utf-8"))
    was_noun = False
    was_adjective = False
    was_prefix  = False
    was_postfix = False
    was_digit = False
    was_digit_prefix = False
    while res:
        word = Word(unicode(res.surface),unicode(res.feature))

        ## 接頭辞は次の名詞に繋ぐ
        if was_prefix and word.is_connected():
            result[-1] = result[-1] + word.surface
            was_noun = True
            was_prefix = False
            res = res.next
            continue
        
        ## 接尾辞は一個前が名詞だったら繋ぐ
        if word.is_postfix() and was_noun:
            result[-1] = result[-1] + word.surface
            was_noun = False
            was_prefix = False
            res = res.next
            continue

        ## 数接続の接頭詞の次に数字だったらつなぐ
        if was_digit_prefix and word.is_digit():
            result[-1] = result[-1] + word.surface
            was_digit = True
            was_digit_prefix = False
            res = res.next
            continue

        ## 数字の次に助数詞が来たらつなげる
        if was_digit and word.is_numerative():
            result[-1] = result[-1] + word.surface
            was_digit = False
            was_noun = False
            res = res.next
            continue
            
        was_noun = word.is_connected()

        was_adjective = word.is_adjective_stem()

        was_prefix = word.is_prefix()

        was_postfix = word.is_postfix()

        was_digit = word.is_digit()

        was_digit_prefix = word.is_digit_prefix()

        if was_noun or was_adjective or was_postfix or was_prefix or \
            was_digit_prefix or word.feature.startswith("名詞"):
            result.append(word.surface)

        res = res.next

    for j in xrange(len(result)):
        word = result[j]
        if not word.isdigit() and not is_symbol_only(word):
            worddic[word] = worddic.get(word, 0) + 1

    return worddic

if __name__ == "__main__":
    import sys
    text = sys.argv[1]
    worddic = extract_noun(text)
    for word,num in worddic.items():
        print word,num
