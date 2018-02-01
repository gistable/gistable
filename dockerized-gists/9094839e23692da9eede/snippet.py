import random

def write_data(filename, num_bytes=1000000):
    with open(filename, 'w') as f:
        for _ in range((num_bytes / 1000) + 1):
            f.write(''.join(random.choice('ab') for _ in range(1000)))

def read_chunks(filename, num_bytes=1000):
    with open(filename, 'r') as f:
        while True:
            s = f.read(num_bytes)
            if s == '':
                break
            yield s

def characters(chunks):
    for chunk in chunks:
        for c in chunk:
            yield c

def compress(stream):
    prev = ''
    count = 1
    for c in stream:
        if c == prev:
            count += 1
        else:
            yield prev + str(count)
            prev = c
            count = 1
    if prev:
        yield prev + str(count)

def chunk(iterable, num_bytes=1000):
    acc = []
    bytes = 0
    for piece in iterable:
        acc.append(piece)
        bytes += len(piece)
        if bytes >= num_bytes:
            data = ''.join(acc)
            yield data
            acc = []
            bytes = 0
    data = ''.join(acc)
    if data:
        yield data

def main():
    write_data('tmp.txt', 100000)
    with open('output.txt', 'w') as f:
        for data in chunk(compress(characters(read_chunks('tmp.txt')))):
            f.write(data)

if __name__ == '__main__':
    main()
