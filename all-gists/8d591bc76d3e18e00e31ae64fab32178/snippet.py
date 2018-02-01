def checker(code, restricted):
    r = set(restricted)
    c = set(code)
    chars = {*'\t\n', *map(chr, range(32, 127))}
    if c == chars - r:
        print('Good to go!')
    else:
        if r & c:
            print('Illegal characters: {}'.format(''.join(r & c)))
        if chars - r - c:
            print('Leftover characters: {}'.format(''.join(sorted(chars - r - c))))
