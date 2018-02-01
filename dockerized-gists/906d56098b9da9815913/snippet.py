#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

def _randnum(f, m):
    num = random.randint(1, 9)
    if f != 0: num = _randdecimel(num, f)
    if m != 0: num = _randminus(num, m)
    return num

def _randdecimel(num, f):
    return num if random.randint(0, f) != 0 else float(format(random.random(), '.1f')) + float(num)

def _randminus(num, m):
    return num if random.randint(0, m) != 0 else num * -1

def _judge(q):
    stack = []
    q = list(q)
    while len(q) > 0:
        stack.append(q.pop(0))
        if not stack[-1].isdigit() and len(stack[-1]) == 1:
            obj = stack.pop()
            num = float(stack.pop(-1))
            if   obj == '+': ans = float(stack.pop()) + num
            elif obj == '-': ans = float(stack.pop()) - num
            elif obj == '*': ans = float(stack.pop()) * num
            elif obj == '/':
                if num == 0:
                    return False
                else:
                    ans = float(stack.pop()) / num
            stack.append(ans)
    if stack[0] < 0 and stack[0] - int(stack[0]) != 0:
        stack[0] -= 1
    return True

def gen(d, f=0, m=0):
    flo = f
    mns = m

    digit = d if d % 2 != 0 else d + 1
    q = [] # 問題
    num = [_randnum(flo, mns) for j in range(int(digit / 2 + 1))]
    obj = [['+', '-', '*', '/'][random.randint(0,3)] for j in range(int(digit / 2))]
    n1, n2 = 0, 0 # 数字/符号の数
    while len(q) < digit:
        if len(num) == 0:
            q += obj # 数字が尽きた場合
            break
        if n1 - n2 < 2:
            q.append(num.pop())
            n1 += 1
        else:
            if random.randint(0, 1) == 0:
                q.append(num.pop())
                n1 += 1
            else:
                q.append(obj.pop())
            n2 += 1
    if _judge(map(str, q)): return " ".join(map(str, q))
    else: return gen(d, f, m)