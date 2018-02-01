class MyList(list):
    def __and__(self, other):
        op = str(bin(other)[2:])
        op = op.zfill(len(self))[::-1]
        acc = []
        for count,i in enumerate(op):
            if int(i):
                acc.append(self[count])
        return acc

    def __rand__(self,other):
        return self.__and__(other)

if __name__=='__main__':
    '''
    A simple example that uses & operator for combining elements of a list
    '''

    l = MyList([1,2,3,4,5])
    for i in range(2**len(l)):
        print l & i