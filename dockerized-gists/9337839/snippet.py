def Fletcher16(string):
    a = map(ord,string)
    b = [sum(a[:i])%255 for i in range(len(a)+1)]
    return (sum(b) << 8) | max(b)
def Fletcher32(string):
    a = map(ord,string)
    b = [sum(a[:i])%65535 for i in range(len(a)+1)]
    return (sum(b) << 16) | max(b)
def Fletcher64(string):
    a = map(ord,string)
    b = [sum(a[:i])%4294967295 for i in range(len(a)+1)]
    return (sum(b) << 32) | max(b)