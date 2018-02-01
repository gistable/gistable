import sys
from StringIO import StringIO

def parse_rtf(f):
    d = f.read()
    # \rtf & \shp 
    if d.find('\x7b\x5c\x72') != -1 and d.find('\x5c\x73\x68\x70') != -1  and d.find('\x5c\x73\x70') != -1:
        addr = d.find('\x5c\x73\x76') 
        if addr != -1:
            f.seek(addr)
            flag = 0
            while(1):
                try:
                    byte = f.read(1)
                except:
                    # breaks if end of file is found
                    return None
                if byte == ';':
                    flag = flag + 1
                if flag == 2:
                    return f.tell()
        return None 
    else:
        return None

def extract_sc(f, addr):
    f.seek(addr)
    b = f.read(2)
    buff = ''
    while(1):
        try:
            buff = buff + chr(int(b,16))
        except ValueError:
            return buff
        b = f.read(2)

def xor_check():

    return

def countup_check():

    return 

def countdown_check():

    return 

      
def main():
        if len(sys.argv) < 2:
            print 'usage: rtf-carv.py <bad.rtf>' 
            print 'output: binary shellcode in sc.bin'
            return
        else:
            try:
                f = open(sys.argv[1], 'rb')
            except Exception:
                print '[ERROR] CAN NOT OPEN FILE'
                return
            a = parse_rtf(f)
            if a == None:
                print 'RTF Signature not found'
                return 
            sc = extract_sc(f,a)
            try: 
                out = open('sc.bin', 'wb+')
            except Exception:
                print '[Error] COULD NOT WRITE SHELLCODE'
            print '\t[SUCESS] Shellcode written to sc.bin'
            out.write(sc)
            out.close()
            
if __name__ == '__main__':
   main()