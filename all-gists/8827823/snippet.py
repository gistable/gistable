def sign_factor(coords, matrix):
    """
    Return the sign factor of the item in a matrix with
    the coordinates specified by 'coords'.
    """
    if (coords[0] % 2 == 0) != (coords[1] % 2 == 0):
        return -1
    else:
        return +1

def minor(coords, matrix):
    """
    Return the minor of the item in a matrix with
    the coordinates specified by 'coords'.
    """
    minor = []
    for i, row in enumerate(matrix):
        if i != coords[0]:
            minor_row = []
            for j, item in enumerate(row):
                if j != coords[1]:
                    minor_row.append(item)
            minor.append(minor_row)
    return minor

def determinant(matrix):
    """
    Return the determinant of a matrix.
    """
    d = 0
    if len(matrix) == 1:
        return matrix[0][0]
    for i in range(len(matrix[0])):
        d += matrix[0][i] * sign_factor((0, i), matrix) * determinant(minor((0, i), matrix))
    return d

A = [[1, 1, 2],
     [3, 3, 5],
     [6, 7, 7]]

print determinant(A)