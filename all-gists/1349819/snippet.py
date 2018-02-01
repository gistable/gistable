def NewTorIP():
    s = socket.socket()
    s.connect(('localhost', 9051))	
    s.send("AUTHENTICATE\r\n")
    r = s.recv(1024)
    if r.startswith('250'):
        s.send("signal NEWNYM\r\n")
        r = s.recv(1024)
        if r.startswith('250'):
            return True
        else:
            return False
    else:
        return False