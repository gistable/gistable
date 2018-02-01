#!/usr/bin/python

# The MIT License
#
# Copyright 2017 Ashung.hung@gmail.com
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall
# be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.




# A python script for convert Sketch file to other version.
# Support Sketch file version greater than 43.
#
# Convert to 43
# $ python convert_sketch_file_other_version.py demo.sketch
#
# Convert to 43.1
# $ python convert_sketch_file_other_version.py demo.sketch 1




import zipfile
import re
import os
import sys

sketchMateData = [
    {
        'appVersion': '43',
        'build': '38999',
        'version': '88',
        'commit': '8533cf0311420996142d259236c1d7bd484f48c8'
    },
    {
        'appVersion': '43.1',
        'build': '39012',
        'version': '88',
        'commit': '335a30073fcb2dc64a0abd6148ae147d694c887d'
    },
    {
        'appVersion': '43.2',
        'build': '39069',
        'version': '88',
        'commit': '2ac3f43dc64a2b7982dc85b584be457e7bbba129'
    },
    {
        'appVersion': '44',
        'build': '41411',
        'version': '91',
        'commit': '149712aeb51bf07cefb5bb6d603b26c4dccfff9d'
    },
    {
        'appVersion': '44.1',
        'build': '41455',
        'version': '91',
        'commit': '10b2b021ddaac63eb3f52ce0b42edfb625ca194b'
    },
    {
        'appVersion': '45',
        'build': '43475',
        'version': '92',
        'commit': '62a429066b6505d0a6a211f8b74e8c5a38b40e00'
    },
    {
        'appVersion': '45.1',
        'build': '43504',
        'version': '92',
        'commit': '50f81cddca44938a07151f71e393545983779bf1'
    },
    {
        'appVersion': '45.2',
        'build': '43514',
        'version': '92',
        'commit': 'c871c6c3fa8a2bc8ee8592fd0f4db2b9a32687dc'
    }
]

sketchFile = os.path.join(os.getcwd(), sys.argv[1])

metaDataIndex = 0
if len(sys.argv) > 2:
    metaDataIndex = int(sys.argv[2]) if int(sys.argv[2]) < len(sketchMateData) - 1 else 0

appVersion = sketchMateData[metaDataIndex]['appVersion']
build = sketchMateData[metaDataIndex]['build']
version = sketchMateData[metaDataIndex]['version']
commit = sketchMateData[metaDataIndex]['commit']

if zipfile.is_zipfile(sketchFile):

    archive = zipfile.ZipFile(sketchFile, 'r')
    meta = archive.read('meta.json')

    # change meta.json
    meta = re.sub(r'"commit":"[0-9a-f]{40}"', '"commit":"' + commit + '"', meta)
    meta = re.sub(r'"appVersion":"[0-9\.]*"', '"appVersion":"' + appVersion + '"', meta)
    meta = re.sub(r'"build":[0-9]{5,}', '"build":' + build, meta)
    meta = re.sub(r'"version":[0-9]{2,}', '"version":' + version, meta)
    meta = re.sub(r'"saveHistory":\["NONAPPSTORE\.[0-9]{5,}"\]', '"saveHistory":["NONAPPSTORE.' + build + '"]', meta)

    # save a temp mate.json
    tmpFile = os.path.join(os.getcwd(), '.meta.json')
    with open(tmpFile, 'w') as file:
        file.write(meta)

    # create new sketch file
    convertedSketchFile = os.path.splitext(sketchFile)[0] + '_save_as_' + appVersion + os.path.splitext(sketchFile)[1]
    convertedArchive = zipfile.ZipFile(convertedSketchFile, 'w')

    # write temp meta.json to new sketch file
    convertedArchive.write(tmpFile, 'meta.json')
    os.remove(tmpFile)

    # move files inside old sketch file to new one
    for item in archive.infolist():
        if (item.filename != 'meta.json'):
            buffer = archive.read(item.filename)
            convertedArchive.writestr(item, buffer)
    convertedArchive.close()

    archive.close()

    print('Save to "' + convertedSketchFile + '".')

else:

    print('None a open format Sketch file.\nThis is a file create with Sketch that under version 43.')
