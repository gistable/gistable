import requests

def frombits(s):
    bts = (int(s[i:i+8], 2) for i in range(0, len(s), 8))
    return str(bytearray(bts))
        
def tobits(s):
    return ''.join(bin(b)[2:].zfill(8) for b in bytearray(s))

def storebit(bit):
    val = 'true' if bit == '1' else 'false'
    res = requests.post('https://api.booleans.io', data={'val': val}).json()
    return res['id']

def storestr(valstr):
    bits = tobits(valstr)
    ids = ','.join(map(storebit, bits))
    return ids

def getbit(bit_id):
    res = requests.get('https://api.booleans.io/'+bit_id).json()
    return '1' if res['val'] else '0'

def getstr(bits_ids):
    print frombits(''.join(map(getbit, bits_ids.split(','))))
