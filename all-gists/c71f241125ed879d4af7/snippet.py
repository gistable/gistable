#!/usr/bin/env python

import random
import sys
import time
import Image

#ROW_AMT = 11185
ROW_AMT = 285
COL_AMT = 290
MID = COL_AMT / 2
BOARD = [[0 for _ in range(COL_AMT)] for __ in range(ROW_AMT)]
CHAR = "+"
SPACE = "."
#CHAR = "\xe2\x97\x89"
#CHAR = "\xe1\x9A\x88"
#CHAR = "\xe2\x96\xbe"
PADDING = COL_AMT * 10
RANDMID = random.randint(0, MID-1)

def setup(n):
  BOARD[0][MID] = 1

def getRGB(v):
  if v == 1:
    return (255,255,255)
  else:
    return (0, 0, 0)

def printPadding():
  for P in range(PADDING):
    if P != 0 and P % COL_AMT == 0:
      sys.stdout.write('\n')
    else:
      printLine(0)
  sys.stdout.write('\n')

def printLine(v):
  #CHAR = "_"
  #SPACE = " "
  CHAR = random.choice(['+', 'A', '-', 'Z', '\\', '*', '^'])
  SPACE = random.choice(['.', ',', ' ', ' ', ' ', ' '])
  sys.stdout.write(CHAR) if v == 1 else sys.stdout.write(SPACE)


def myHandsAreClaws(y, rule):

    if y % 3 == 0:
      rule -= 1
    elif y % 5 == 0:
      rule -= 2
    else:
      rule += 2

    BOARD[y][MID] = 1
    #BOARD[y][MID+1] = 0
    #BOARD[y][MID-1] = 0

    #BOARD[y][MID-RANDMID] = 1
    #BOARD[y][MID+RANDMID] = 1
    #BOARD[y][MID-RANDMID/2] = 1
    #BOARD[y][MID+RANDMID/2] = 1
    #BOARD[y][RANDMID/2] = 1
    #BOARD[y][COL_AMT - RANDMID/2] = 1

    return rule

def main():
  if len(sys.argv) == 3:
    rule = 18
  else:
    rule = int(sys.argv[1])
  setup(rule)

  printPadding()

  # Render Image:
  img = Image.new('RGB', (COL_AMT, ROW_AMT), "black")
  pixels = img.load()

  for x in range(COL_AMT):
    printLine(BOARD[0][x])
  sys.stdout.write('\n')

  for y in range(ROW_AMT):

    #rule = myHandsAreClaws(y, rule)

    #time.sleep(0.008);
    time.sleep(0.002);
    sys.stdout.write("Rule #: {}\t\t".format(rule))

    if y == 0: continue
    for x in range(COL_AMT):

      left = BOARD[y-1][(x-1) % COL_AMT]
      mid = BOARD[y-1][x]
      right = BOARD[y-1][(x+1) % COL_AMT]
      bits = int('0b{}{}{}'.format(left, mid, right), 2)

      ruleBits = [int(b) for b in '{0:08b}'.format(rule)][::-1]

      for i, r in enumerate(ruleBits):
        if r == 1 and bits == i:
          BOARD[y][x] = 1

      pixels[x, y] = getRGB(BOARD[y][x])

      printLine(BOARD[y][x])
    sys.stdout.write('\n')

    #if BOARD[y][MID] == BOARD[y-1][MID]:
    #  #rule += 4 #rule += 3
    #  rule += 7

    #rule = int('0b' + ''.join([str(x) for x in BOARD[y][MID-8:MID]]), 2)
    #BOARD[y][MID] = 1
    #if BOARD[y-1] == BOARD[y]: rule = rule ^ 0xff

  printPadding()
  img.show()

if __name__ == '__main__':
  main()