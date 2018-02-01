def rsa(m, key, n):
    h = '{:x}'.format(pow(int(m.encode('hex'), 16), key, n))
    return ('0'+h if len(h) % 2 else h).decode('hex')
