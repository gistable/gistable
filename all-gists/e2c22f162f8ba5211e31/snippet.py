#!/usr/bin/python
# Invoke this script with a Swift file containing an XCTestCase and it will
# generate an implementation for the `allTests` variable required for
# XCTestCaseProvider conformance on Linux

import sys
import re

inFile = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin

testNames = []

for line in inFile:	
	matchObj = re.search(r'func (test.*)\(\)', line)

	if matchObj:
		testNames.append(matchObj.group(1))

print "var allTests: [(String, () throws -> Void)] {"
print "    return ["
for testName in testNames:
	print "        (\""+testName+"\", "+testName+"),"
print "    ]"
print "}"
