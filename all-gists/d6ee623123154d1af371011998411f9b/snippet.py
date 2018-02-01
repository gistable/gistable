from typing import List


Vector = List[float]

def somar(multi: float, vetor: Vector) -> Vector:
  return [multi * i for i in vetor]


result: List[float] = somar(2.0, [1,2,3,4,5])
  