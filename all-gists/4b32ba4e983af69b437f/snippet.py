import sys
print('loading file')
pgnfile = open(sys.argv[1], 'rb')
glob = pgnfile.read()
print('done')
print('convertingbytes')
pgn = ''
for b in glob:
    c = chr(b)
    pgn += c
print('done')
del(glob)
data = ""
recording = True
terminationchar = ""
termpairs = [['[', ']'], ['(', ')'], ['{', '}']]
def charfilter(char):
    global terminationchar
    global recording
    global termpairs
    if recording:
        if char in '{[(':
            recording = False
            for pair in termpairs:
                if pair[0] == char:
                    terminationchar = pair[1]
    else:
        if char == terminationchar:
            recording = True
print('filtering data')
for char in pgn:
    charfilter(char)
    if recording:
        data += char

print('done')
point = 0
squares = []
xs = 0
print('calculating')
while point != len(data):
    if data[point] == 'x':
        xs += 1
        square = data[point + 1:point + 3]
        notinsquares = True
        for pair in squares:
            if pair[0] == square:
                notinsquares = False
                pair[1] += 1
        if notinsquares:
            squares.append([square, 1])
    point += 1

total = 0
for pair in squares:
    total += pair[1]

print('Total captures:', total)

for pair in squares:
    print(pair[0] + ',', str(pair[1]) + ',', str(int(pair[1] / total * 100)) + '%')