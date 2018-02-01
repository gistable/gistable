#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random

global compareCount

def swap(arr, l, r):
    temp = arr[l]
    arr[l] = arr[r]
    arr[r] = temp

def partition(arr, l, r):
    if (r - l) < 1:
        return
    
    randomIndex = random.randint(l, r)  #randint(l, r) -> [l, r]
    swap(arr, randomIndex, r)
    
    i = l - 1
    for j in range(l, r+1):  #range(l, r) -> [l, r)
        if arr[j] <= arr[r]:
            i = i + 1
            swap(arr, i, j)

    partition(arr, l, i-1)
    partition(arr, i+1, r)

def quickSort(arr):
    partition(arr, 0, len(arr)-1)

def randomList(length):
    l = []
    for i in range(0, length):
        l.append(random.randint(0, 100))
    return l

# Snippet From Python Cookbook
# Also available at the link below : 
# http://zh.wikipedia.org/zh-cn/%E5%BF%AB%E9%80%9F%E6%8E%92%E5%BA%8F#Python
def qsort(L): 
    if len(L) <= 1: return L 
    return qsort([lt for lt in L[1:] if lt < L[0]]) + L[0:1] + \
                        qsort([ge for ge in L[1:] if ge >= L[0]])

if __name__ == '__main__':
    for i in range(0, 5):
        l = randomList(random.randint(5,15))
        print('Before sort : ', l)
        quickSort(l)
        print('After  sort : ', l)
