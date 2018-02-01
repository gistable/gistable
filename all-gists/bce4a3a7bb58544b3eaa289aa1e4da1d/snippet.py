"""
By Arda Mavi
github.com/ardamavi

Using:
# Encoder:
If you want to encode your sentence, use this command: encode(<your_sentence>)
Example:
Your Sentence: "ar ma"
Return: [[0.0, 0.6538461538461539], [0.46153846153846156, 0.0]]

# Decoder:
If you want to decode your encoded sentence, use this command: decode(<encoded_sentence>)
Example:
Your Encoded Sentence: [[0.0, 0.6538461538461539], [0.46153846153846156, 0.0]]
Return: "ar ma"

! Note: For lower case.
"""

# Encode:
def l2n(x):
    return (ord(x)-97)/26

def w2v(w):
    w_v = []
    for l in w:
        w_v.append(l2n(l))
    return w_v

def s2v(s):
    s_v = []
    for w in s.split(' '):
        s_v.append(w2v(w))
    return s_v

def encode(sentence):
    return s2v(sentence)

# Decode

def n2l(x):
    return chr(int(x*26+97))

def v2w(v):
    w = ''
    for f in v:
        w = w + n2l(f)
    return w

def v2s(s_v):
    s = ''
    for v in s_v:
        s = s + v2w(v) + ' '
    return s[:len(s)-1]

def decode(metrix):
    return(v2s(metrix))