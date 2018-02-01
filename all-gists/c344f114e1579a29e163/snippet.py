from struct import unpack, iter_unpack
from collections import namedtuple
import os

def read_file_list(f, entry_num):
    def decode(data, index):
        for (n, item) in enumerate(data):
            item = item[0]
            item -= 39
            item ^= 0xA5
            item -= (27 + index + n)
            yield item % 256
    def to_str(data):
        res_string = ''
        for item in data:
            if item >= 0x21 and item <= 0x7E:
                res_string += '{:c}'.format(item)
        return res_string
    def to_int(data):
        result = 0
        data = list(data)[::-1]
        for item in data:
            result <<= 8
            result += item
        return result
    result = []
    last_offs, offs = 0, 0
    Item = namedtuple('Item', 'name offset size')
    for index in range(0, entry_num * 17, 17):
        last_offs = offs
        raw = list(decode(iter_unpack('B', f.read(17)), index))
        name = to_str(raw[:13])
        offs = to_int(raw[13:])
        if index > 1:
            pos = index // 17 - 1
            result[pos] = Item(result[pos][0], result[pos][1], offs - last_offs)
        result.append(Item(name, offs, 0))
    result.pop()
    return result

if __name__ == '__main__':
    with open('data.fil', 'rb') as f:
        num = unpack('i', f.read(4))[0] ^ 0x3BD7A59A
        files = read_file_list(f, num)
        for file in files:
            # if not os.path.exists('export'):
                # os.makedirs('export')
            with open('{}'.format(file.name), 'wb') as w:
                f.seek(file.offset)
                w.write(f.read(file.size))