#Written by: @JamesHabben

from luhn import *

cardNumber = '4???123412341234'
var_digits = {}
for i, c in enumerate(cardNumber):
    if c == '?':
        var_digits[i] = 0

def digit_inc():
    iterdig = iter(var_digits)
    var_digits[var_digits.keys()[0]] = var_digits.values()[0] + 1
    last_key = var_digits.keys()[0]
    iterdig.next()
    for k in iterdig:
        if var_digits[last_key] > 9:
            var_digits[last_key] = 0
            var_digits[k] = var_digits[k] + 1
        last_key = k
    if var_digits.values()[-1] > 9:
        return False
    else:
        return True

def format_digit():
    temp_card = list(cardNumber)
    for k in var_digits:
        temp_card[k] = str(var_digits[k])
    return "".join(temp_card)

if verify(format_digit()):
    print format_digit()
while digit_inc():
    if verify(format_digit()):
        print format_digit()
