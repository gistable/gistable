def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs
    
class BFRMQ():
    def __init__(self, arr):
        self.arr_ = arr

    def query(self, left, right):
        return min(self.arr_[left:right+1])

class BlockRMQ():
    def __init__(self, arr, micro_factory=BFRMQ, macro_factory=BFRMQ):
        self.arr_ = arr
        self.micro_factory_ = micro_factory
        self.macro_factory_ = macro_factory

        # preprocess
        self.block_arr_ = split(self.arr_, 3)
        print "block arry: ", self.block_arr_
        self.block_min_arr_ = [min(x) for x in self.block_arr_]
        self.macro_rmq_ = macro_factory(self.block_min_arr_)
        self.mini_rmqs_ = [micro_factory(x) for x in self.block_arr_]

        print self

    def query(self, left, right):
        block_left = left / 3
        block_right = right / 3
        
        result = self.mini_rmqs_[block_left].query(left - block_left * 3, min(2, right - block_left * 3))

        if (left <= block_left * 3 and right >= (block_right+1) * 3):
            result = min(result, self.macro_rmq_.query(block_left, block_right))
            
        if (left < 3 and right >= 3):
            result = min(result, self.mini_rmqs_[block_left].query(left, 2))
            
        if (right >= (block_right + 1) * 3):
            result = min(result, self.mini_rmqs_[block_right+1].query(0, right - (block_right+1) * 3))

        return result


q = BlockRMQ([1, 2, 3, 4, 5], BFRMQ, BFRMQ)
print q.query(1, 1)
print q.query(1, 4)
print q.query(2, 4)
print q.query(2, 3)

q2 = BlockRMQ([1, 2, 3, 4, 5], BFRMQ, BlockRMQ)
print q2.query(1, 1)
print q2.query(1, 4)
print q2.query(2, 4)
print q2.query(2, 3)
