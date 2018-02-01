import numpy as np, itertools

data = [510.06, 100, 792.99, 301.50, 170.02, 100.00, 309.89, 312.46, 100.00, 201.03, 111.43, 422.74, 100.00, 100.00, 768.20, 100.00, 100.00, 301.78, 100.00]
target = 2922.06

for L in range(0, len(data)+1):
  for subset in itertools.combinations(data, L):
    if np.isclose(sum(subset),target):
      print(sum(subset), subset)