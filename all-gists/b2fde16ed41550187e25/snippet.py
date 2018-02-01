class Prime:
    def __init__(self):
        self.found = []
        self.i = 2
        self.idx = -1 #Iterator用

    def __getitem__(self, n):           #n番目の素数が見つかるまでwhileを回す
        while len(self.found) < n+1:    #すでに見つかっていれば定数時間ですむ
            if not any(self.i % x == 0 for x in self.found):
                self.found.append(self.i)
            self.i += 1
        return self.found[n]

    def __iter__(self): #ループのためにイテレータとして参照された場合
        self.idx = -1
        return self

    def __len__(self):  #無限という建前なので長さはない
        return None

    def __next__(self): #__next__ (Python 2ならnext) でイテレータにもなれる
        self.idx += 1
        return self.__getitem__(self.idx)   #idx番目の素数を返すだけ
        
p = Prime()

for i in range(10): #添字表現による参照
    print('Prime number #%d = %d' % (i+1, p[i]))

for n in p: #Iteratorによるループ(無限に回るので途中で打ち切る必要がある)
    print('n = ', n)
    if n > 50: break
