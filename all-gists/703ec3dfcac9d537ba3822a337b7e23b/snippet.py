__author__ = "wasi0013"

import urllib2
from bs4 import BeautifulSoup
import re
from fractions import gcd
import random


def affine_encrypt(text, a, b, m=26):
    """
    takes string as text and decrypts it with the key a,b
    >>> affine_encrypt("AFFINE CIPHER",5,8)
    'IHHWVC SWFRCP'
    """
    if gcd(a, m) == 1:
        return "".join(i if i == " " else chr((a*(ord(i.lower())-97) + b)%m + 65) for i in text if i.isalpha() or i == " ")

def affine_decrypt(text, a, b, m=26):
    """
    takes string as text and decrypts it with the key a,b
    >>> affine_decrypt("IHHWVC SWFRCP",5,8)
    'AFFINE CIPHER'
    """
    coprimes = [i for i in range(1, m) if gcd(m, i) == 1]
    c = None
    for num in coprimes:
        if (num * a)%m == 1:
            c = num
    return "".join(i if i == " " else chr((c*(ord(i.lower())-97-b))%m + 65) for i in text if i.isalpha() or i == " ")

def emo_maker(emo_list, text):
    """
    returns: unicode-emoji string
    takes a list of emoji and a text string as argument
    encrypts the text as unicode-emoji
    """
    output = ""
    a = random.randint(2, 25)
    while gcd(a,26)!=1:
        a = random.randint(2,25)
    b = random.randint(1, 128)
    encrypted_text = affine_encrypt(text, a, b)
    for i in encrypted_text:
        num = ord(i)
        output += emo_list[num]
        
    return emo_list[a]+emo_list[b]+output


def emo_decode(emo_list, emo_text):
    """
    returns: decrypted text (in Uppercase Letter)
    decrypts the unicode-emoji strings as texts
    """
    a = emo_list.index(emo_text[0])
    b = emo_list.index(emo_text[1])
    encrypted_text = ""
    for i in emo_text[2::]:
        encrypted_text += chr(emo_list.index(i))
    return affine_decrypt(encrypted_text, a, b)


def get_emo_list(page):
    """
    emoji parser: collects emoji from the page
    returns: list of unicode-emoji
    """
    soup = BeautifulSoup(page)
    table = soup.find('table')
    #emo_dict= dict()

    emo_list = list()
    for row in table.findAll('tr')[1:]:
        col = row.findAll('td')

        #TODO replace it with better solution
        try:
            #name of the emo
            #text = col[15].get_text()
            #emo_dict[col[3].find("img").get("alt","")] = text
            emo_list.append(col[3].find("img").get("alt", ""))
        except:
            pass

    return emo_list


def main():
    
    url = ('http://unicode.org/emoji/charts/full-emoji-list.html')
    page = urllib2.urlopen(url).read()

    #filename = "Moo/index.html"
    #page = ''.join(open(filename,'r').readlines())
    
    emo_list = get_emo_list(page)
    encrypted_msg = emo_maker(emo_list, "Lame Jokes") #*codes
    
    decrypted_msg = emo_decode(emo_list, encrypted_msg)
    print(encrypted_msg)
    print(decrypted_msg)


if __name__ == '__main__':
    main()