#!/usr/bin/env python2

from random import randint

def generate_imei(incomplete_imei):
    luhn_sum = 0
    imei_digits = []

    for i in xrange(0,14):
        # Pull each digit from the TAC, generate missing numbers with rand()
        try:
            digit = incomplete_imei[i]
        except IndexError:
            digit = randint(0, 9)

        # Add digits to IMEI
        imei_digits.append(str(digit))

        # Double every odd indexed digit
        if (i % 2 != 0):
            digit = digit * 2

        # Split digits and add, ex: "14" becomes "1+4"
        for component in str(digit):
            luhn_sum = luhn_sum + int(component)

    remainder = luhn_sum % 10
    check_digit = 0 if (remainder == 0) else (10 - remainder)
    imei_digits.append(str(check_digit))
    return "".join(imei_digits)

#tac = "10457816123456"
#tac = "49015420323751"
tac = "104578"
imei = generate_imei(tac)

print("TAC:  %s" % tac)
print("IMEI: %s" % imei)
