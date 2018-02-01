# O(n), n = total number of bits
def count_bits1(num):
  count = 0
  while num > 0:
    if num % 2 == 1:
      count += 1

    num //= 2

  return count

# O(t), t = number of bits set to 1
def count_bits2(num):
  count = 0
  while num > 0:
    num &= num - 1
    count += 1

  return count

# O(?)
def count_bits3(num):
  return bin(num).count('1')

# O(1)
def popcount_with_table():
  table = [0] * 2**16
  for index in range(len(table)):
    table[index] = (index & 1) + table[index >> 1]

  def popcount(num):
    return (table[num & 0xffff] + table[(num >> 16) & 0xffff])

  return popcount

count_bits4 = popcount_with_table()

def bit_distance(num1, num2):
  return count_bits4(num1 ^ num2)

assert bit_distance(10, 10) == 0
assert bit_distance(10, 11) == 1
assert bit_distance(-5, -6) == 1
assert bit_distance(31, 14) == 2

# count_bits1: 4.87s average
# count_bits2: 2.34s average
# count_bits3: 1.01s average
# count_bits4: 0.90s average
for i in range(1000000):
  bit_distance(i, i * 2)