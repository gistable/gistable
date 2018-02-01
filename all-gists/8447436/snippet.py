class Matriz(object):
    def __init__(self, mat):
        self.mat = mat

    def linhas(self):
        return len(self.mat)

    def colunas(self):
        return len(self.mat[0])

    def __len__(self):
        return len(self.mat)

    def __getitem__(self, index):
        return self.mat[index]

    def __mul__(self, m2):
        A = self
        B = Matriz(m2.mat)

        if A.colunas() == B.linhas():
            return [ 
                [sum(A[i][k] * B[k][j] 
                    for k in xrange(len(B))) 
                    for j in xrange(len(B[0]))]
                for i in xrange(len(A))
                ]
        else:
            return 'matrix multiplication is not valid'


mat1 = [[1, 2, 3],
        [3, 2, 1],
        [2, 1, 3]]

mat2 = [[4, 5, 6],
        [6, 5, 4],
        [4, 6, 5]]

M1 = Matriz(mat1)
M2 = Matriz(mat2)

print M1 * M2




