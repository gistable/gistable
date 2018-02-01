#coding:utf-8

from turtle import *

def main():
    for i in range(2):
        moji(i)

def moji(i):
    if i == 1:
        up()
        goto(-20,280)
        down()
        write("うまい")
        up()
        goto(0,270)
        down()
        write("棒")
    else:
        up()
        goto(-35,290)
        down()
        waku()

def waku():
    fillcolor('yellow')
    begin_fill()
    for i in range(1,5):
        if i % 2 == 0:
            forward(100)
            right(90)
        else:
            forward(45)
            right(90)
    end_fill()

if __name__ == "__main__":
    main()
    raw_input("type enter")