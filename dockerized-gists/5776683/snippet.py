def repmat(matrixA, rowFinal, colFinal):
  return [matrixA[i] * colFinal for i in range(len(matrixA))] * rowFinal