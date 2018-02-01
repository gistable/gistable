#!/usr/bin/python

from string import maketrans

rot13trans = maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
 
def rot13(text):
    return text.translate(rot13trans)

def main():
    txt = "hello world"
    print rot13(txt)

if __name__ == "__main__":
    main()