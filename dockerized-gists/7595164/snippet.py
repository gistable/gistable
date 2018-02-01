import re
import hashlib
import base58
from pycoin.ecdsa import generator_secp256k1, public_pair_for_secret_exponent

def bytetohex(byteStr):
        return ''.join( [ "%02X" % x for x in byteStr ] ).strip()

litecoin = [b"\x30", b"\xb0"]
bitcoin = [b"\x00", b"\x80"]

cointype = litecoin

walletHandle = open("C:/Users/alex/Downloads/litecoin-0.8.5.1-win32-setup/data/wallet.dat", "rb")
wallet = walletHandle.read()

privKeys=set(re.findall(b'\x70\x6F\x6F\x6C(.{52})', wallet))

print("Found %d privKeys" % len(privKeys))

for key in privKeys:
    key = key[20:]
    
    public_x, public_y = public_pair_for_secret_exponent(generator_secp256k1, int(bytetohex(key), 16))
    compressed_public_key = bytes.fromhex("%02x%064x" % (2 + (public_y & 1), public_x))


    #https://en.bitcoin.it/wiki/Technical_background_of_Bitcoin_addresses

    m = hashlib.new('ripemd160')
    m.update(hashlib.sha256(compressed_public_key).digest())
    ripe = m.digest() # Step 2 & 3

    extRipe = cointype[0] + ripe # Step 4

    chksum = hashlib.sha256(hashlib.sha256(extRipe).digest()).digest()[:4] # Step 5-7

    addr = extRipe + chksum # Step 8
    print("Address:", base58.b58encode(addr))



    # compressed wallet import format http://sourceforge.net/mailarchive/forum.php?thread_name=CAPg%2BsBhDFCjAn1tRRQhaudtqwsh4vcVbxzm%2BAA2OuFxN71fwUA%40mail.gmail.com&forum_name=bitcoin-development
    key = cointype[1] + key + b"\x01"
    
    chksum = hashlib.sha256(hashlib.sha256(key).digest()).digest()[:4]

    addr = key + chksum # Step 8
    print("Private Key:", base58.b58encode(addr),"\n")
    
walletHandle.close()
