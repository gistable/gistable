# -*-coding: utf-8 -*-
import sys
import os

num = sys.argv[1]  # num is the amount of *.ts files


def add(x):
    """'x' is the amount of *.ts
    This function should add all other .ts combined into '1.ts'
    """
    os.popen("touch all.ts")
    x = int(x)
    i = 1
    while i <= x:
        command = "cat " + str(i) + ".ts " + ">> all.ts"
        try:
            os.popen(command)
        except:  # 如果没有当前.ts, 打印出错误并跳过
            print "There is no " + i + ".ts"
        i += 1
    return True


if __name__ == '__main__':
    add(num)
