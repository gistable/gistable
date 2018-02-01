import sys
import HTMLParser
import re

htmlparser = HTMLParser.HTMLParser()
numwords = 2


def main(filename):
    with open(str(filename)) as infile:
        for line in infile:
            processLine(line)


def processLine(line):
    line = line.strip()
    if(hasData(line)):
        data = stripLine(line)
        if data != "":
            splitdata = data.split(" ")
            if len(splitdata) >= numwords:
                processWords(splitdata)


def processWords(words):
    for currword in range(len(words)):
        print words[currword]


def hasData(line):
    if line.startswith(("*", "!", "|", ";", "<", "{", "[", "&", ".")):
        return False
    if line.startswith("==") and line.endswith("=="):
        return False
    return True


def stripLine(line):
    line = line.decode('utf8')
    data = htmlparser.unescape(line).lower()  # decode htmlcodes and make lowercase
    data = re.sub('\[\[(?:[^\]|]*\|)?([^\]|]*)\]\]', '\1', data)  # turn [[Link]] to link
    p = re.compile('\{\{*.*\}\}')
    data = p.sub('', data)  # remove {{data}}
    p = re.compile('<.*?>')
    data = p.sub(' ', data)  # remove <ref>
    data = re.sub('http.*? ', '', data)
    data = re.sub("[^A-Za-z0-9 ]", "", data)  # remove anything extra
    data = data.strip()
    return data


if __name__ == '__main__':
    main(sys.argv[1])