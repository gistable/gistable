# coding=utf-8
#
# python 中文输出处理
#
# 参考 http://bbs.chinaunix.net/thread-4076265-1-1.html
# 


def pad(str, width = 0, direct = 'left') :
    count = 0

    for s in str:
        if ord(s) > 127:
            count += 1

    width += (count/3)

    if direct == 'right' or direct == 'r':
        return str.rjust(width)
    else :
        return str.ljust(width)

# test
print '|' + pad('姓名', 20) + '|' + pad('地址', 20) + '|'
print '+' + '-'*20 + '|' + '-'*20 + '|'
print '|' + pad('陈X', 20) + '|' + pad('杭州4路', 20) + '|'
print '|' + pad('陈X', 20, 'r') + '|' + pad('杭州17路', 20, 'r') + '|'

# output:
#
# |姓名                |地址                |
# +--------------------|--------------------|
# |陈X                 |杭州4路             |
# |                 陈X|            杭州17路|