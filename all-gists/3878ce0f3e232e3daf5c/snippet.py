#!/usr/bin/python

from variety.plugins.IQuoteSource import IQuoteSource
import subprocess, re
from locale import gettext as _

class FortuneSource(IQuoteSource):
    @classmethod
    def get_info(cls):
        return {
            "name": "Fortunes",
            "description": _("Displays quotes using the UNIX fortune program"),
            "author": "Dan Jones",
            "version": "0.1"
            }

    def supports_search(self):
        return False

    def get_random(self):
        fortune = subprocess.check_output(['fortune'])
        q = fortune.split('--')
        quote = q[0].strip()
        if len(q) > 1:
            s = q[1].strip()
            m = re.search('(.+), +"?(.+)"?',s)
            if m:
                author = m.group(1)
                sourceName = m.group(2)
            else:
                author = s
                sourceName = None
        else:
            author = None
            sourceName = None

        r = {
            "quote": quote,
            "author": author,
            "sourceName": sourceName,
            "link": None
            }

        return [r]
    
    def get_for_author(self, author):
        return []

    def get_for_keyword(self, keyword):
        return []

### Read Me
#
# First be sure that fortune is installed and in your PATH
# Copy this file to ~/.config/variety/plugins/quotes
# Restart variety
#
###
# 
# Gist: https://gist.github.com/goodevilgenius/3878ce0f3e232e3daf5c
#
### BEGIN LICENSE
# Copyright (c) 2014 Dan Jones
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
### END LICENSE

