"""
Uncipher Cisco type 7 ciphered passwords
Usage: python uncipher.py <pass> where <pass> is the text of the type 7 password

Example:
$ python uncipher.py 094F4F1D1A0403
catcat
"""
import fileinput
import sys

global key
key = [0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 0x66, 0x6f, 0x41,
 0x2c, 0x2e, 0x69, 0x79, 0x65, 0x77, 0x72, 0x6b, 0x6c,
 0x64, 0x4a, 0x4b, 0x44, 0x48, 0x53, 0x55, 0x42]

def uncipher(ciphertext):
    try:
        index = int(pw[:2],16)
    except ValueError:
        return ''
    pw_text = ciphertext[2:].rstrip()
    pw_hex_values = [pw_text[start:start+2] for start in range(0,len(pw_text),2)]
    pw_chars = [chr(key[index+i] ^ int(pw_hex_values[i],16)) for i in range(0,len(pw_hex_values))]
    pw_plaintext = ''.join(pw_chars)
    return pw_plaintext

try:
    for pw in fileinput.input():

        print uncipher(pw)
except:
    pw = sys.argv[1]
    print uncipher(pw)

