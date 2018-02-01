import unittest

from solution import wow_such_much, count_doge_words


class TestDoge(unittest.TestCase):
    def test_suchmuch_to_0(self):
        self.assertEqual(wow_such_much(1, 0), [])

    def test_suchmuch_to_1(self):
        self.assertEqual(wow_such_much(1, 1), [])

    def test_suchmuch_to_2(self):
        self.assertEqual(wow_such_much(1, 2), ['1'])

    def test_suchmuch_to_16(self):
        self.assertEqual(
            wow_such_much(1, 16),
            ['1', '2', 'such', '4', 'much', 'such', '7', '8', 'such', 'much',
             '11', 'such', '13', '14', 'suchmuch'])

    def test_with_simple_sentence(self):
        self.assertEqual(3, count_doge_words("wow much hard such difficult"))

    def test_with_empty_sentence(self):
        self.assertEqual(0, count_doge_words(""))

    def test_with_parasite_sentence(self):
        self.assertEqual(6, count_doge_words('wow lol so such much very'))

    def test_with_glued_parasite_words(self):
        self.assertEqual(0, count_doge_words('wowlolsosuchmuchvery'))

    def test_with_repeating_parasite_words(self):
        self.assertEqual(5, count_doge_words('wow hard wow much such difficult much'))

    def test_with_more_space_between_parasites(self):
        self.assertEqual(6, count_doge_words('wow  lol    so  such   much      very'))


if __name__ == '__main__':
    unittest.main()