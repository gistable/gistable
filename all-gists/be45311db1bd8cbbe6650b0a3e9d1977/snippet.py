from fractions import Fraction

def invert(matrix):
    n = len(matrix)
    inverse = [[Fraction(0) for col in range(n)] for row in range(n)]

    for i in range(n):
        inverse[i][i] = Fraction(1)

    for i in range(n):
        for j in range(n):
            if i != j:
                if matrix[i][i] == 0:
                    return false
                ratio = matrix[j][i] / matrix[i][i]
                for k in range(n):
                    inverse[j][k] = inverse[j][k] - ratio * inverse[i][k]
                    matrix[j][k] = matrix[j][k] - ratio * matrix[i][k]

    for i in range(n):
        a = matrix[i][i]
        if a == 0:
            return false
        for j in range(n):
            inverse[i][j] = inverse[i][j] / a
    return inverse


def answer(pegs):
    if len(pegs) < 2:
        return [-1, -1]

    if len(pegs) == 2:
        x = (Fraction(pegs[1] - pegs[0]) / Fraction(3)) * Fraction(2)
        if (x.numerator < 1) or (x.numerator < x.denominator):
            return [-1, -1]

        return [x.numerator, x.denominator]

    matrix = []
    rowNum = 0
    deltas = []
    for loc in pegs:
        deltas.append(Fraction(pegs[rowNum + 1] - pegs[rowNum]))

        if rowNum == 0:
            row = [Fraction(2), Fraction(1)] + [Fraction(0)] * (len(pegs) - 3)
            matrix.append(row)
        elif rowNum == len(pegs) - 2:
            row = [Fraction(1)] + [Fraction(0)] * (len(pegs) - 3) + [Fraction(1)]
            matrix.append(row)
            break
        else:
            row = [Fraction(0)] * rowNum + [Fraction(1), Fraction(1)] + [Fraction(0)] * (len(pegs) - rowNum - 3)
            matrix.append(row)
        rowNum = rowNum + 1

    inverse = invert(matrix)
    if not(inverse):
        return [-1, -1]

    # Validate all gears
    for i in range(1, len(pegs)-1):
        y = Fraction(0)
        for j in range(len(pegs)-1):
            y = y + inverse[i][j] * deltas[j]
        if (y.numerator < 1) or (y.numerator < y.denominator):
            return [-1, -1]

    x = Fraction(0)
    for i in range(len(pegs)-1):
        x = x + inverse[0][i] * deltas[i]

    x = x * Fraction(2)

    if (x.numerator < 1) or (x.numerator < x.denominator):
        return [-1, -1]

    return [x.numerator, x.denominator]

print(answer([1, 2]))