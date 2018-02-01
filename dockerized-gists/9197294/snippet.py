def RC4(data, key):
    x = 0
    s = range(256)
    for i in range(256):
        x = (x + s[i] + ord(key[i % len(key)])) % 256
        s[i], s[x] = s[x], s[i]
    x = y = 0
    out = ""
    for c in data:
        x = (x + 1) % 256
        y = (y + s[x]) % 256
        s[x], s[y] = s[y], s[x]
        out += chr(ord(c) ^ s[(s[x] + s[y]) % 256])
    return out
