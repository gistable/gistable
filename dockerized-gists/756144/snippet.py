#!/usr/bin/env python
# coding:utf-8

'''
Created by ben on 2010-12-27
Copyright (c) 2011 http://sa3.org All rights reserved.
'''

import re
import unittest

def clly(value):
    def process(obj):
        if obj.group(1) in ['demo','whatever']:
            return value
        return '''<a href="%s" ><img src="http://img.ly/%s/content" /></a>''' %(
            obj.group(0),
            obj.group(1)
        )
    return re.sub(r'http://cl.ly/([a-zA-Z0-9]+)',process,value)

class TestClly(unittest.TestCase):
    def test_clly(self):
        self.assertEqual(clly(''),'')
        self.assertEqual(clly('aaaa'),'aaaa')
        self.assertEqual(clly('http://cl.ly/abc'),
                         '<a href="http://cl.ly/abc" ><img src="http://img.ly/abc/content" /></a>')
        self.assertEqual(clly('http://cl.ly/demo'),'http://cl.ly/demo')
        self.assertEqual(clly('abcdsdfhttp://cl.ly/123\n\n\nhttp://cl.ly/123'),
                         'abcdsdf<a href="http://cl.ly/123" ><img src="http://img.ly/123/content" /></a>\n\n\n<a href="http://cl.ly/123" ><img src="http://img.ly/123/content" /></a>')
if __name__ == "__main__":
    unittest.main()