import socket, struct, os, binascii, base64, subprocess
import telnetlib   

import base58

def readline(sc, show = True):
    res = ""
    while len(res) == 0 or res[-1] != "\n":
        data = sc.recv(1)
        if len(data) == 0:
            print repr(res)
            raise Exception("Server disconnected")
        res += data
        
    if show:
        print repr(res[:-1])
    return res[:-1]

def read_until(sc, s):
    res = ""
    while not res.endswith(s):
        data = sc.recv(1)
        if len(data) == 0:
            print repr(res)
            raise Exception("Server disconnected")
        res += data
        
    return res[:-(len(s))]
    
def read_all(sc, n):
    data = ""
    while len(data) < n:
        block = sc.recv(n - len(data))
        if len(block) == 0:
            print repr(data)
            raise Exception("Server disconnected")
        data += block

    return data

def I(n):
    return struct.pack("<I", n)
    
def Q(n):
    return struct.pack("<Q", n)

def gen_addr(prefix):
    for a in '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz':
        for b in '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz':
            res = base58.b58decode((prefix+a+b).ljust(33, "1"))
            res = base58.b58encode_check(res[0:21])
            if res.startswith(prefix):
                return res
                
    return None

while True:
    sc = socket.create_connection(("178.62.22.245", 41662))

    read_until(sc, "Are you ready? [Y]es or [N]o:")
    sc.send("Y\n")
    read_until(sc, "Send a BTC valid address that starts with ")
    prefix = read_until(sc, ":")
    print prefix
    res = gen_addr(prefix)
    print res
    if res == None:
        sc.close()
        continue
    
    sc.send(res + "\n")

    while True:
        print read_until(sc, "| n = ")
        n = int(readline(sc))

        proc = subprocess.Popen(["d:\\temp\\yafu\\yafu-x64.exe", "factor(%d)" % n], stdout=subprocess.PIPE)

        ntest = 1
        factors = {}

        res = proc.communicate()[0]
        #print res
        
        for line in res.split("\r\n"):
            if " = " in line:
                parts = line.split()
                if len(parts) != 3 or parts[2] == "1":
                    continue
                    
                f = int(parts[2])
                ntest *= f
                if f not in factors:
                    factors[f] = 0
                factors[f] += 1
                
        print "found valid factors:", ntest == n
        if ntest != n:
            sc.close()
            break
            
        print factors
        target = []
        for f in factors:
            target.append(factors[f])

        print target

        a = 1
        b = 2
        for t in target:
            a *= ((t + 1) * 2) - 1
            b *= t + 1
            
        res = (a - b + 1) / 2
        print "result", res
        sc.send(str(res) + "\n")
        

#sc.send("1\n")

# t = telnetlib.Telnet()                                                  
# t.sock = sc
# t.interact()  

while True:
    data = sc.recv(16384)
    if len(data) == 0:
        break
    for line in data.split("\n"):
        print repr(line)
    