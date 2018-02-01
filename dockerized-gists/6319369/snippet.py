#!/usr/bin/env python
# -*- mode: python, coding: utf-8 -*-
#
# This incredible piece of code makes git a bit Polish, a bit Western Ukrainian,
# пше прошу пана
# Joke is based on fact that 'git' is 'пше' in qwerty/йцукен layouts
#
# (c) 2013 Alexander Solovyov under terms of WTFPL

import sys
from subprocess import call


# commit <- цомміт, дамміт :(
table = dict(zip(u'а б в г д е ë ж з и й к л м н о п р с '
                 u'т у ф х ц ч ш щ ь ы ъ э ю я'.split(),
                 u'a b v g d e e zh z i j k l m n o p r s '
                 u't u f h c ch sh sch \' y \' e yu ya'.split()))
table[u'і'] = 'i'
table[u'є'] = 'e'
table[u'ї'] = 'yi' # їєлд -> yield :-)


def transletter(l):
    if l.lower() not in table:
        return l
    n = table[l.lower()]
    return n.upper() if l.isupper() else n


def transliterate(s):
    return ''.join(map(transletter, s.decode('utf-8')))


def main(args):
    args = map(transliterate, args)
    return call(['git'] + args)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    print 'Usage: пше цомманд оптионс -> git command options'
    print ''
    print 'Пше гіт версіон 0.1'
    print ''
    print 'Используйте транслитерированные команды, например:'
    print ' - пше цоммит -м "инитиал цоммит"'
    print ' - пше цомміт -м "інітіал цомміт"'
    print ' - пше лог'
    print ' - пше пуш'
