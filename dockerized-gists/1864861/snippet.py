import string
import sys

# list of valid characters to use in the shortener slug
CHARSET = string.digits + string.lowercase + string.uppercase

# convert a numeric id to a url-shortener-type slug
def shorty(id):
    slug = ""
    while id > 0:
        remainder = id % len(CHARSET)
        # perform integer division on the id
        id /= len(CHARSET)
        slug += CHARSET[remainder]
    return slug

# do an inverse conversion from a url-shortener-type slug to numeric id
def inv_shorty(slug):
    id = 0
    for idx, char in enumerate(slug):
        id += pow(len(CHARSET), idx) * CHARSET.find(char)
    return id

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s id' % (sys.argv[0])
    else:
        print shorty(int(sys.argv[1]))
