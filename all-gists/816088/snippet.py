# wtf8.py
import codecs

def encode(input, errors='strict'):
    return input.encode('utf-8', errors).decode('latin-1', errors).encode('utf-8', errors), len(input)

def decode(input, errors='strict'):
    return input.decode('utf-8', errors).encode('latin-1', errors).decode('utf-8', errors), len(input)

class StreamWriter(codecs.StreamWriter):
    encode = encode

class StreamReader(codecs.StreamReader):
    decode = decode

def find_codec(codec_name):
    if codec_name.lower() == 'wtf-8':
        return (encode, decode, StreamReader, StreamWriter)
    return None

codecs.register(find_codec)

if __name__ == "__main__":
    msg = u"I \u2665 Unicode"
    print "In your terminal's encoding:", msg
    print "In glorious WTF-8:", msg.encode('wtf-8')
