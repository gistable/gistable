# coding=utf-8
"""
Slugify for Chinese

没有优化多音字
优化多音字的项目有：
https://github.com/jiedan/chinese_pinyin
"""
import re
import unidecode

def slugify(str):
    return re.sub(r'\s+', '-', unidecode.unidecode(str).lower().strip())


# Test
print slugify(u"测试")
# >>> ce-shi
