def ping(server, port):
    ''' Check if a server accepts connections on a specific TCP port '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        s.close()
        return True
    except socket.error:
        return False