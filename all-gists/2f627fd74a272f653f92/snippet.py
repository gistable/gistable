global heap
global currSize

def parent(i): #returns parent index of ith index
    return i/2

def left(i): #returns left child of ith index
    return 2*i

def right(i): #returns right child of ith index
    return (2*i + 1)
    
def swap(a, b): #to swap a-th and b-th elements in heap
    temp = heap[a]
    heap[a] = heap[b]
    heap[b] = temp

def insert(elem):
    global currSize
    
    index = len(heap)
    heap.append(elem)
    currSize += 1
    par = parent(index)
    flag = 0
    while flag != 1:
        if index == 1: #we have reached the root of the heap
            flag = 1
        elif heap[par] > elem: #if parent index is larger than index of elem, then elem has now been inserted into the right place
            flag = 1
        else: #swaps the parent and the index itself
            swap(par, index)
            index = par
            par = parent(index)
    print heap

def extractMax():
    global currSize
    if currSize != 0:
        maxElem = heap[1]
        heap[1] = heap[currSize] #replaces root element with the last element
        heap.pop(currSize) #deletes last element present in heap
        currSize -= 1 #reduces size of heap
        maxHeapify(1)
        return maxElem

def maxHeapify(index):
    global currSize
    
    lar = index
    l = left(index)
    r = right(index)

    #print heap

    #finds the larger child of the index; if larger child exists, swaps it with the index
    if l <= currSize and heap[l] > heap[lar]:
        lar = l
    if r <= currSize and heap[r] > heap[lar]:
        lar = r
    if lar != index:
        swap(index, lar)
        maxHeapify(lar)

def buildHeap():
    global currSize
    for i in range(currSize/2, 0, -1): #third argument in range() shows increment factor, here -1
        print heap
        maxHeapify(i)
    currSize = len(heap)-1
    
def heapSort():
    for i in range(1, len(heap)):
        print heap
        heap.insert(len(heap)-i, extractMax()) #inserting the greatest element at the back of the array
    currSize = len(heap)-1
    
heap = []
i = 0
s = 'blah'
print "Welcome to heap program. Enter your list below:"
while s != '':
    s = raw_input('--> ')
    if s != '':
        heap.append(int(s))
currSize = len(heap)
heap.insert(0, 0)
print "Building heap..."
buildHeap()
print heap