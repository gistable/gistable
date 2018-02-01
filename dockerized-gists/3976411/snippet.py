# -*- encoding: utf-8 -*-

import unittest

class TestSomething(unittest.TestCase):
    def test_unicode(self):
        self.assertEqual(u'Русский', u'Текст')

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    unittest.main()
