import socket

ss = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
ss.bind(('localhost', 8080))
ss.listen(5)
conn, addr = ss.accept()
#conn.send("Hello World")
print conn.recv(4096)
conn.shutdown(socket.SHUT_RDWT)
ss.shutdown(socket.SHUT_RDWR)
ss.close()

#Pythonで基礎の基礎みたいなsocket書きたかった。
#socketちゃんと閉じないし漂うクソコード臭