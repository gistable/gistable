import urllib2

def xiami_decode(s):
    s = s.strip()
    if not s:
        return False
    result = []
    line = int(s[0])
    rows = len(s[1:]) / line
    extra = len(s[1:]) % line
    s = s[1:]
    
    for x in xrange(extra):
        result.append(s[(rows + 1) * x:(rows + 1) * (x + 1)])
    
    for x in xrange(line - extra):
        result.append(s[(rows + 1) * extra + (rows * x):(rows + 1) * extra + (rows * x) + rows])
    
    url = ''
    
    for x in xrange(rows + 1):
        for y in xrange(line):
            try:
                url += result[y][x]
            except IndexError:
                continue
    
    url = urllib2.unquote(url)
    url = url.replace('^', '0')
    return url

if __name__ == '__main__':
    url = '8h2xt%5F287.tFi%5E%%3%mt%a2E75515pp2mF%7EE7E3%Fi82111863f.1F8%769A3n14%26_5%.e6%25913'
    print(xiami_decode(url))
