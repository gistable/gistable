#!/usr/bin/env python

"""
Utility fonction to convert from one form to an other
"""
def to_bits(length, N):
  return [int(i) for i in bin(N)[2:].zfill(length)]

def from_bits(N):
  return int("".join(str(i) for i in N), 2)

def str_to_bits(s):
  return [b for i in s for b in to_bits(8, ord(i))]

def bits_to_hex(b):
  return hex(from_bits(b)).rstrip("L")

def to_xor_formula(val):
  result = []
  for i in val:
    if i == 0:
      result.append(XorFormula(["0"]))
    else:
      result.append(XorFormula(["1"]))
  return result

"""
Those are the modified crc, xor and hmac fonction that will perform 
their operation symbolically.
"""
def crc(mesg):
  mesg += CONST
  shift = 0
  while shift < len(mesg) - 64:
    ov = mesg[shift]
    for i in range(65):
      if CRC_POLY[i].fields[0] == "1":
        mesg[shift + i] = mesg[shift + i].xor(ov)
    shift += 1

  return mesg[-64:]

def xor(x, y):
  return [g.xor(h) for (g, h) in zip(x, y)]


def hmac(h, key, mesg):
  return h(xor(key, OUTER) + h(xor(key, INNER) + mesg))

"""
Those are the original crc, xor and hmac function.
"""

def crcn(mesg):
  mesg += CONST
  shift = 0
  while shift < len(mesg) - 64:
    if mesg[shift]:
      for i in range(65):
        mesg[shift + i] ^= CRC_POLY[i]
    shift += 1
  return mesg[-64:]

INNER = to_bits(8, 0x36) * 8
OUTER = to_bits(8, 0x5c) * 8

def xorn(x, y):
  return [g ^ h for (g, h) in zip(x, y)]

def hmacn(h, key, mesg):
  return h(xorn(key, OUTER) + h(xorn(key, INNER) + mesg))


"""
Guassian matrix solver for XOR operation.
"""
def solve(equation, result):
  system = []

  for i in range(64):
    if "1" in equation[i].fields:
      result[i] ^= 1

    r = [0]*64
    for k in range(64):
      if "K" + str(k) in equation[i].fields:
        r[k] = 1

    system.append(r)

  for i in range(64):
    good_row = -1

    for j in range(i, 64):
      if system[j][i] == 1:
        good_row = j
        break

    if good_row == -1:
      break

    tmp = system[i]
    system[i] = system[good_row]
    system[good_row] = tmp

    tmp = result[i]
    result[i] = result[good_row]
    result[good_row] = tmp

    for j in range(64):
      if i != j and system[j][i] == 1:
        system[j] = xorn(system[j], system[i])
        result[j] ^= result[i]

  return result

"""
Holds the symbolic result that's a series of XOR.
"""
class XorFormula:
  fields = []
  def __init__(self, a):
    self.fields = a

  def xor(self, a):
    c_field = self.fields[:]

    for g in a.fields:
      # When we add xor value, if the value is already present, 
      # they cancel each other (K0 ^ K0 ^ 1 == 1)
      if g in c_field:
        c_field.remove(g)
      else:
        c_field.append(g)
    return XorFormula(c_field)

  def __str__(self):
    return " ^ ".join(self.fields)

  def __repr__(self):
    return self.__str__()

# We set the KEY to be 64 symbolics variables K0 up to K63.
KEY = []
for i in range(64):
  KEY.append(XorFormula(["K" + str(i)]))

CRC_POLY = to_bits(65, (2**64) + 0xeff67c77d13835f7)
CONST = to_bits(64, 0xabaddeadbeef1dea)

INNER = to_bits(8, 0x36) * 8
OUTER = to_bits(8, 0x5c) * 8

PLAIN_1 = "zupe zecret"
PLAIN_2 = "BKPCTF"

# We need to transform the other existing input to be 
# symbolic too.
INNER = to_xor_formula(INNER)
OUTER = to_xor_formula(OUTER)
CRC_POLY = to_xor_formula(CRC_POLY)
CONST = to_xor_formula(CONST)
PLAIN_1_V = to_xor_formula(str_to_bits(PLAIN_1))
PLAIN_2_V = to_xor_formula(str_to_bits(PLAIN_2))

# We perform the crc computation of PLAIN_1.
# Since the KEY was set as a series of symbolic 
# variable, the result will be the a series of 
# 64 equations that will have 0, 1, K0, K1, ...
# K63 as their components.
equation = hmac(crc, KEY, PLAIN_1_V)
result = to_bits(64, 0xa57d43a032feb286)

# We solve the equation system that we obtained with
# the result that was given in the problem. This 
# will give us the value of the KEY.
KEY = solve(equation, result)

# We use this key to compute the HMAC-CRC of PLAIN_2
CRC_POLY = to_bits(65, (2**64) + 0xeff67c77d13835f7)
CONST = to_bits(64, 0xabaddeadbeef1dea)

INNER = to_bits(8, 0x36) * 8
OUTER = to_bits(8, 0x5c) * 8

# Print the final flag !
print "BKPCTF{" + bits_to_hex(hmacn(crcn, KEY, str_to_bits(PLAIN_2))) + "}"