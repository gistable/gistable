#-*- coding:utf-8 -*-
__author__ = 'bluele'

import unittest


class SuffixArray(object):

    def __init__(self, string):
        self.string = string
        self.pairs = self.parse(string)

    def parse(self, string):
        """ 指定した文字列の最後尾に'$'を付与しarrayを分割する
        """
        pairs = list(self.___parse(string))
        return sorted(pairs)

    def ___parse(self, string):
        limit = len(string)
        cur = 0
        _string = string + '$'
        while limit >= cur:
            yield _string[cur:], cur
            cur += 1

    def search(self, target):
        # 出現した位置のリスト
        locations = list()
        cur = self.__bin_search(target)
        if cur is False:
            return locations

        locations.append(self.pairs[cur][1])
        r_char_cur = self.__get_right_neighbor_cursor(cur, target)
        l_char_cur = self.__get_left_neighbor_cursor(cur, target)

        while r_char_cur is not None:
            locations.append(self.pairs[r_char_cur][1])
            r_char_cur = self.__get_right_neighbor_cursor(r_char_cur, target)

        while l_char_cur is not None:
            locations.append(self.pairs[l_char_cur][1])
            l_char_cur = self.__get_left_neighbor_cursor(l_char_cur, target)

        return sorted(locations)

    def __get_right_neighbor_cursor(self, cur, target):
        cur += 1
        if 0 <= cur < len(self.pairs):
            string = self.pairs[cur][0]
            if string.startswith(target):
                return cur
        return None

    def __get_left_neighbor_cursor(self, cur, target):
        cur -= 1
        if 0 <= cur < len(self.pairs):
            string = self.pairs[cur][0]
            if string.startswith(target):
                return cur
        return None

    def __bin_search(self, target):
        length = len(self.pairs) - 1
        low = 0
        high = length
        cur = length / 2
        while 0 < cur < length:
            cur = (low + high) /2
            string = self.pairs[cur][0]
            if string.startswith(target): # 接頭辞一致
                return cur
            elif target > string:
                low = cur + 1
            else:
                high = cur - 1
        return False

    def __getitem__(self, item):
        return self.pairs[item][0]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(self.pairs)

    def __repr__(self):
        return self.__unicode__()


class SuffixArrayTest(unittest.TestCase):

    def setUp(self):
        self.s_array = SuffixArray("abracatabrabra")

    def testSearch(self):
        self.assertListEqual(self.s_array.search("abr"), [0, 7, 10])
        self.assertListEqual(self.s_array.search("a"), [0, 3, 5, 7, 10, 13])
        self.assertListEqual(self.s_array.search("t"), [6])


def main():
    unittest.main()


if __name__ == "__main__":
    main()