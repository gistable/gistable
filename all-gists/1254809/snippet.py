#!/usr/bin/python

import re
import os
import pprint
import subprocess
import time
import Levenshtein

########################################################################

theLicenses = {
'BSD (4 clause)': '''Copyright (c) {year}, {copyright_holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the {organization}.
4. Neither the name of the {organization} nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY {COPYRIGHT_HOLDER} ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL {COPYRIGHT_HOLDER} BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.''',

'BSD (3 clause)': '''Copyright (c) {year}, {copyright_holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the {organization} nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL {COPYRIGHT_HOLDER} BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.''',

'BSD (2 clause)': '''Copyright {year} {copyright_holder}. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY {COPYRIGHT_HOLDER} ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL {COPYRIGHT_HOLDER} OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of {copyright_holder}.''',

'MIT': '''Copyright (C) {year} by {copyright_holders}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.''',
    }

########################################################################

def edit(path):
    subprocess.call(['/usr/local/bin/bbedit', '-w', path])

thePatterns = [
    r'''^(?P<filename>.+\.[h|m|c|cpp])
    (?P<project>.+)

    Created\ by\ (?P<creator>.+?)\ on\ (?P<date>.+).
    Copyright\ (?P<copyright_year>.+?)\ (?P<copyright_holder>.+?)\.\ All\ rights\ reserved\.'''
    ]

thePatterns = [thePattern.replace('\n', '\\n') for thePattern in thePatterns]

thePatterns = [re.compile(thePattern, re.MULTILINE | re.VERBOSE) for thePattern in thePatterns]

theRoot = '/Users/schwa/Development/Source/Git/github_touchcode_public/TouchLogging'

def files(inPath):
    for root, dirs, files in os.walk(inPath):
        for theSkipDirectory in ['.git', '.svn', '.hg', 'Externals', 'ISO-8601-parser-0.5']:
            if theSkipDirectory in dirs:
                del dirs[dirs.index(theSkipDirectory)]
        for theFile in files:
            theExtension = os.path.splitext(theFile)[1]
            if theExtension in ['.h', '.m']:
                yield os.path.join(root, theFile)

theMetadataSet = set()

for thePath in files(theRoot):
    theFullPath = os.path.join(theRoot, thePath)
    theLines = file(theFullPath).readlines()

    theHeaderLineCount = 0
    theHeaderLines = []
    for theLine in theLines:
        if theLine[0:2] == '//':
            theHeaderLines.append(theLine[2:].strip())
            theHeaderLineCount += 1
        else:
            break
    theHeader = '\n'.join(theHeaderLines)
    theHeader = theHeader.strip()

    for thePattern in thePatterns:
        theMatch = thePattern.match(theHeader)
        if theMatch:
            break
    if not theMatch:
        print '#### No match on: %s' % thePath
        edit(thePath)
        continue

    theMetadata = dict(theMatch.groupdict())

    s = ','.join(['%s:%s' % (k, theMetadata[k]) for k in sorted(theMetadata.keys())])
    theMetadataSet.add(s)


    if len(theHeader[theMatch.end(0):]) > 0:
        theFileLicense = theHeader[theMatch.end(0):].strip()
        theLicenseScores = []
        for theLicenseName, theLicense in theLicenses.items():
            theLicenseScores.append((Levenshtein.distance(theFileLicense, theLicense), theLicenseName))
        theLicenseScores.sort()
        if theLicenseScores[0][1] != 'BSD (2 clause)':

            theNewLicense = theLicenses['BSD (2 clause)']

            theMetadata['year'] = '2011'
            theMetadata['COPYRIGHT_HOLDER'] = 'JONATHAN WIGHT'

            s = ''

            theNewLicense = theNewLicense.format(**theMetadata)
            s += '''//
//  {filename}
//  {project}
//
//  Created by {creator} on {date}.
'''.format(**theMetadata)

            theLicenseLines = theNewLicense.split('\n')
            theLicenseLines = ['//  ' + theLine for theLine in theLicenseLines]
            theLicenseLines = [theLine.rstrip() for theLine in theLicenseLines]
            s +=  '\n'.join(theLicenseLines)
            s += '\n'
            s +=  ''.join(theLines[theHeaderLineCount:])

            print 'Updating', thePath

            file(theFullPath,'w').write(s)



#   if theMatch.groupdict()['project'] in ['AnythingBucket']:
#       edit(thePath)

if theMatch.groupdict()['copyright_holder'] != 'toxicsoftware.com':
    edit(thePath)

# for s in theMetadataSet:
#     print s
