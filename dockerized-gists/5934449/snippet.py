# -*- coding: utf-8 -*-
#!/usr/bin/python
from cssutils.util import Item

#==============================================================================
# Written following the example by Graham.
# IMHO, there was problem with the stack pop method. Even though
# tail pointed to the previous object in the linked list right after pop,
# the tail kept pointing at the popped Item.
#Written by Amit
#==============================================================================

import random

printLimit = 5


class Node(object):

    def __init__(self, other=None):
        self.other = other
        self.next = None
        self.previous = None

    def __str__(self):
        return str(self.other)


class List(object):

    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, value):
        newNode = Node(value)
        if self.head == None:
            self.head = newNode
            self.tail = newNode
        else:
            self.tail.next = newNode
            newNode.previous = self.tail
            self.tail = newNode

    def __str__(self):
        someString = ""
        current = self.head
        while current != None:
            someString = someString + " " + str(current.other)
            current = current.next
        return someString


class Queue(List):
    def enqueue(self, value):
        self.append(value)

    def dequeue(self):
        self.temp = self.head
        self.head = self.head.next
        return self.temp


class Stack(List):
    def push(self, value):
        self.append(value)

    def pop(self):
        self.temp = self.tail
        print self.tail.previous
        self.tail = self.tail.previous
        self.tail.next = None
        return self.temp


def execute_queue():
    print "==Queue Time=="
    queue = Queue()
    for i in xrange(0, printLimit):
        queue.append(str(i))
    print "Current Queue"
    print queue
    print "Enqueuing 420"
    queue.enqueue(100)
    print queue
    print "dequeuing"
    queue.dequeue()
    print queue


def execute_stack():
    stack1 = Stack()
    for i in xrange(0, printLimit):
        stack1.append(i)
    print "==Stack Time=="
    print stack1
    print "Push Time!"
    stack1.push(420)
    print stack1
    print "Pop Time"
    stack1.pop()
    print stack1
    print "Push Time Again!"
    stack1.push(425)
    print stack1
    print "Pop Time"
    stack1.pop()
    print stack1


def main():
    list1 = List()
    for i in xrange(0, printLimit):
        list1.append(str(i))
    print list1
    execute_queue()
    execute_stack()

if __name__ == '__main__':
    main()
