from array import array
import bisect
import struct
import operator
import sys

class WordList(object):
    def __init__(self, words):
        self.buf = "".join(words)
        self.offsets = array("L", [0])
        self.lengths = array("B", [])
        for i, s in enumerate(words[:-1]):
            self.offsets.append(len(s) + self.offsets[-1])
        for s in words:
            self.lengths.append(len(s))
            
    def __getitem__(self, index):
        start = self.offsets[index]
        end = start + self.lengths[index]
        return self.buf[start:end]
    
    def __len__(self):
        return len(self.offsets)

    def __sizeof__(self):
        return sum(sys.getsizeof(item) for item in (self.buf, self.offsets, self.lengths))
    
    
class Index(object):
    
    def __init__(self, words, offsets, lengths):
        self.words = WordList(words)
        self.offsets = array("L", offsets)
        self.lengths = array("L", lengths)
        
    def search(self, word):
        idx = bisect.bisect_left(self.words, word)
        return idx, self.words[idx], self.offsets[idx], self.lengths[idx]
    
    def __sizeof__(self):
        return sum(sys.getsizeof(item) for item in (self.words, self.offsets, self.lengths))


def load_index(idxfn):
    def _load_index():
        info_struct = struct.Struct(">LL")
        with open(idxfn, "rb") as f:
            data = f.read()
            start = 0
            while True:
                end = data.find("\x00", start)
                if end < 0:
                    break
                info = info_struct.unpack_from(data, end+1)
                yield data[start:end], info[0], info[1]
                start = end + 9
    
    words = list(_load_index())
    words.sort(key=operator.itemgetter(0))
    return Index(*zip(*words))


class Dict(object):
    def __init__(self, idxfn, dictfn):
        self.index = load_index(idxfn)
        self.dictfn = dictfn
        
    def search(self, word):
        _, word2, offset, length = self.index.search(word)
        with open(self.dictfn, "rb") as f:
            f.seek(offset)
            text = f.read(length)
        return word2.decode("utf8") + "\n" + text.decode("utf8")
    
    def __sizeof__(self):
        return sum(sys.getsizeof(item) for item in (self.index, self.dictfn))

if __name__ == "__main__":
    e2c = Dict("sun_dict_e2c.idx", "sun_dict_e2c.dict")
    print "memory:", sys.getsizeof(e2c)
    print e2c.search("python")