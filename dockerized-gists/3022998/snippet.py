# -*- coding:utf-8 -*-

'写了一个简单的支持中文的正向最大匹配的机械分词,其它不用解释了，就几十行代码'
'搜狗词库下载地址：http://vdisk.weibo.com/s/7RlE5'

import string
__dict = {} 

def load_dict(dict_file='words.dic'):
    '加载词库，把词库加载成一个key为首字符，value为相关词的列表的字典'

    words = [unicode(line, 'utf-8').split() for line in open(dict_file)]

    for word_len, word in words:
        first_char = word[0]
        __dict.setdefault(first_char, [])
        __dict[first_char].append(word)
    
    #按词的长度倒序排列
    for first_char, words in __dict.items():
        __dict[first_char] = sorted(words, key=lambda x:len(x), reverse=True)

def __match_ascii(i, input):
    '返回连续的英文字母，数字，符号'
    result = ''
    for i in range(i, len(input)):
        if not input[i] in string.ascii_letters: break
        result += input[i]
    return result


def __match_word(first_char, i , input):
    '根据当前位置进行分词，ascii的直接读取连续字符，中文的读取词库'

    if not __dict.has_key(first_char): 
        if first_char in string.ascii_letters:
            return __match_ascii(i, input)
        return first_char

    words = __dict[first_char]
    for word in words:
        if input[i:i+len(word)] == word:
            return word

    return first_char

def tokenize(input):
    '对input进行分词，input必须是uncode编码'

    if not input: return []

    tokens = []
    i = 0
    while i < len(input):
        first_char = input[i] 
        matched_word = __match_word(first_char, i, input)
        tokens.append(matched_word)
        i += len(matched_word)

    return tokens


if __name__ == '__main__':
    def get_test_text():
        import urllib2
        url = "http://news.baidu.com/n?cmd=4&class=rolling&pn=1&from=tab&sub=0"
        text = urllib2.urlopen(url).read()
        return unicode(text, 'gbk')

    def load_dict_test():
        load_dict()
        for first_char, words in __dict.items():
            print '%s:%s' % (first_char, ' '.join(words))

    def tokenize_test(text):
        load_dict()
        tokens = tokenize(text)
        for token in tokens:
            print token

    tokenize_test(unicode(u'美丽的花园里有各种各样的小动物'))
    tokenize_test(get_test_text())
