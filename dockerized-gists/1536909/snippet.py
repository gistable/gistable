#usage:
#=>python ./un_rwwwshell.py g5mAlfbknz

from binascii import a2b_uu
from sys import argv

tr = {'a':'=','b':"'",'c':')','e':':','d':'(','g':'&','f':';','h':'>','k':',','j':'<','m':'$','l':'#','o':'%','n':'*','q':'!','p':']','s':'"','r':'@','u':'\\','t':'`','v':'-','z':'\n'}
input = list(argv[-1])
print a2b_uu(''.join([tr.get(input[x],input[x]) for x in range(0,len(input))]))