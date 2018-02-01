import os
from Crypto.Cipher import _Blowfish
from struct import pack


def encrypt(infilepath, outfilepath, key):
    """ Encrypt the specified file with the specified
       key and output to the chosen output file."""

    size = os.path.getsize(infilepath)
    infile = open(infilepath, 'rb')
    outfile = open(outfilepath, 'wb')
    data = infile.read()
    infile.close()

    if size % 8 > 0:  # Add padding if size if not divisible by 8
        extra = 8-(size % 8)
        padding = [0]*extra
        padding = pack('b'*extra, *padding)
        data += padding

    revdata = reversebytes(data)
    encrypted_data = encryptbytes(revdata, key)
    finaldata = reversebytes(encrypted_data)
    outfile.write(finaldata)
    outfile.close()


def encryptbytes(data, key):

    cipher = _Blowfish.new(key, _Blowfish.MODE_ECB)
    return cipher.encrypt(data)


def decrypt(infilepath, outfilepath, key):
    """ Decrypt the specified file with the specified
       key and output to the chosen output file"""

    infile = open(infilepath, 'rb')
    outfile = open(outfilepath, 'wb')
    data = infile.read()
    infile.close()

    revdata = reversebytes(data)
    decrypted_data = decryptbytes(revdata, key)
    finaldata = reversebytes(decrypted_data)

    end = len(finaldata) - 1
    while str(finaldata[end]).encode('hex') == '00':
        end -= 1

    finaldata = finaldata[0:end]

    outfile.write(finaldata)
    outfile.close()


def decryptbytes(data, key):

    cipher = _Blowfish.new(key, _Blowfish.MODE_ECB)
    return cipher.decrypt(data)


def reversebytes(data):
    """ Takes data and reverses byte order to fit
        blowfish-compat format. For example, using
        reversebytes('12345678') will return 43218765."""
    data_size = 0
    for n in data:
        data_size += 1

    reversedbytes = bytearray()
    i = 0
    for x in range(0, data_size/4):
        a = (data[i:i+4])
        i += 4
        z = 0

        n0 = a[z]
        n1 = a[z+1]
        n2 = a[z+2]
        n3 = a[z+3]
        reversedbytes.append(n3)
        reversedbytes.append(n2)
        reversedbytes.append(n1)
        reversedbytes.append(n0)

    return buffer(reversedbytes)


'''
############# USES #############
infilepath = 'input.txt'
outfilepath = 'output.txt'
key = "mykey" 

encrypt(infilepath, outfilepath, key)
decrypt(infilepath, outfilepath, key)
'''