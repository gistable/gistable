def find_ngrams(input_list, max_n):
  return [map(lambda x: list(x), zip(*[input_list[i:] for i in range(n)])) for n in range(1, max_n+1)]