#coding:utf-8
import random

def amida_shuffle(line_num, exchange_num):
    lines = range(line_num)
    for i in xrange(exchange_num):
        p = random.randrange(line_num - 1)
        lines[p], lines[p+1] = lines[p+1], lines[p]
    return lines

def range_shuffle(range_num):
    lines = range(range_num)
    random.shuffle(lines)
    return lines

def main():
    try_num = 100
    line_num = 10
    exchange_num = 15

    same_count = [0, 0]

    for i in xrange(try_num):
        amida_list = amida_shuffle(line_num, exchange_num)
        shuffle_list = range_shuffle(line_num)

        for k in xrange(line_num):
            if amida_list[k] == k:
                same_count[0] += 1
            if shuffle_list[k] == k:
                same_count[1] += 1

    print same_count
    # [265, 108]

if __name__ == "__main__":
    main()