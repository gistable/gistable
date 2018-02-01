import re
import sys

def func():
    testme= "The variable is a 0x0f4 dozen of camels and horses. It has to convince Bob to meet alice at 0acdadecf822eeff32aca5830e438cb54aa722e3. The entire conversation is stored at 8BADF00D but then it requires 82 bundles of sockets"
    
    match = re.findall (r'\d[\w*]+[\d*]+[\w*]+' , testme)
    
    print match

def main():
    func()

if __name__=='__main__':
    main()