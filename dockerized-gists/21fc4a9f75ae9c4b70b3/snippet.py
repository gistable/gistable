def parent(i):
    return i/2

def left(i):
    return 2*i

def right(i):
    return (2*i + 1)

class Heap:
    def __init__(self, someList):
        self.heap = someList
        self.currSize = len(someList)
        self.heap.insert(0, 0)

    def swap(self, a, b):
        temp = self.heap[a]
        self.heap[a] = self.heap[b]
        self.heap[b] = temp

    def insert(self, elem):
        
        index = len(self.heap)
        self.heap.append(elem)
        self.currSize += 1
        par = parent(index)
        flag = 0
        while flag != 1:
            if index == 1:
                flag = 1
            elif self.heap[par] > elem:
                flag = 1
            else:
                self.swap(par, index)
                index = par
                par = parent(index)
        
        print self.heap

    def extractMax(self):
        if self.currSize != 0:
            maxElem = self.heap[1]
            self.heap[1] = self.heap[self.currSize]
            self.heap.pop(self.currSize)
            self.currSize -= 1
            self.maxHeapify(1)
            return maxElem

    def maxHeapify(self, index):
        
        lar = index
        l = left(index)
        r = right(index)

        #print heap
        
        if l <= self.currSize and self.heap[l] > self.heap[lar]:
            lar = l
        if r <= self.currSize and self.heap[r] > self.heap[lar]:
            lar = r
        if lar != index:
            self.swap(index, lar)
            self.maxHeapify(lar)

    def buildHeap(self):
        for i in range(self.currSize/2, 0, -1): 
            print self.heap
            self.maxHeapify(i)
        self.currSize = len(self.heap)-1
        print self.heap

    def heapSort(self):
        for i in range(1, len(self.heap)):
            print self.heap
            self.heap.insert(len(self.heap)-i, self.extractMax())
        self.currSize = len(self.heap)-1
        print self.heap