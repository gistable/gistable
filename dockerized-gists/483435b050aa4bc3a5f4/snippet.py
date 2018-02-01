import socket, time
s = socket.socket()
address = ''
port = 5577
r = 0
g = 255
b = 0
keybit = "31".replace(':', '').decode('hex')
keybit += chr(r) + chr(g) + chr(b)
keybit += "00:f0:0f".replace(':', '').decode('hex')
keybit += chr(sum(bytearray(keybit))%256)
print sum(bytearray(keybit[:-1]))%256
print keybit.encode('hex')
try:
    s.connect((address, port))
    s.send("81:8a:8b:96".replace(':', '').decode('hex'))
    s.recv(1000)
    s.send("10:14:0f:08:0d:05:16:15:04:00:0f:8b".replace(':', '').decode('hex'))
    s.recv(1000)
    s.send(keybit)
except:
    print("Could Not Connect (They are finnicy!)")