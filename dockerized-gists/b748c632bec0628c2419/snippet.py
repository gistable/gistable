#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

BASE_TEN = {
   1: ['One', 'Eleven', 'Ten'],
   2: ['Two', 'Twelve', 'Twenty'],
   3: ['Three', 'Thirteen', 'Thirty'],
   4: ['Four', 'Fourteen', 'Forty'],
   5: ['Five', 'Fifteen', 'Fifty'],
   6: ['Six', 'Sixteen', 'Sixty'],
   7: ['Seven', 'Seventeen', 'Seventy'],
   8: ['Eight', 'Eighteen', 'Eighty'],
   9: ['Nine', 'Nineteen', 'Ninety']
}


def print_result(in_text):
    print "{}Dollars".format(in_text)


def check_decimals_and_units(in_text, number, tens):
    if tens >= 2:
        in_text.append(BASE_TEN[tens][2])
    if tens == 1:
        if number > 0:
            in_text.append(BASE_TEN[number][1])
        else:
            in_text.append(BASE_TEN[tens][2])
    if number > 0 and (tens == 0 or tens >= 2):
        in_text.append(BASE_TEN[number][0])


def break_hundreds(number, in_text, base):
    hundreds = 0
    tens = 0
    if number >= 100:
        hundreds = int(number / 100)
        number %= 100
    if number >= 10:
        tens = int(number / 10)
        number %= 10
    if hundreds > 0:
        in_text.append('{}Hundred'.format(BASE_TEN[hundreds][0]))
    check_decimals_and_units(in_text, number, tens)
    in_text.append(base)


def main():
    test_cases = open(sys.argv[1], 'r')
    for test in test_cases.readlines():
        try:
            number = int(test)
        except ValueError:
            continue
        billion = int(number / 1000000000)
        if billion > 0:
            continue
        number %= 1000000000
        million = int(number / 1000000)
        number %= 1000000
        thousands = int(number / 1000)
        number %= 1000
        hundreds = int(number / 100)
        number %= 100
        decimals = int(number / 10)
        number %= 10
        unity = number % 10
        in_text = []
        if million:
            break_hundreds(million, in_text, 'Million')
        if thousands:
            break_hundreds(thousands, in_text, 'Thousand')
        if hundreds > 0:
            in_text.append('{}Hundred'.format(BASE_TEN[hundreds][0]))
        check_decimals_and_units(in_text, unity, decimals)
        if in_text:
            print_result(''.join(in_text))

    test_cases.close()

if __name__ == '__main__':
    main()
