class Solution:
    # @param A : list of integers
    # @param B : integer
    # @return a list of integers
    def dNums(self, A, B):
        mapOfNums = {}
        count = 0
        ptr = -1
        res = []
        if B > len(A) :
            return res
        else :
            for i in range(0, len(A)):
                if mapOfNums.get(A[i], 0) == 0:
                    count = count + 1
                    mapOfNums[A[i]] = 1
                else :
                    mapOfNums[A[i]] += 1
                if i >= B :
                    ptr += 1
                    mapOfNums[A[ptr]] -= 1
                    if mapOfNums[A[ptr]] == 0 :
                        count -= 1
                if i >= B - 1:
                    res.append(count)
        return res
                