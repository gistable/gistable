#! /usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2013 Hannes Bretschneider

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, fileinput

def main(): 
    for line in fileinput.input(inplace=True):
        if '</HTML>' in line.upper():
            print """<script type="text/javascript">
function hideElements(elements, start) {
    for (var i = 0, length=elements.length; i < length; i++) {
        if (i >= start) {
            elements[i].style.display = "none";
        }
    }
}
var input_elements = document.getElementsByClassName('input');
hideElements(input_elements, 0);
var prompt_elements = document.getElementsByClassName('prompt');
hideElements(prompt_elements, 0);
</script>
""",
        print line,

if __name__ == '__main__':
   main()
   
