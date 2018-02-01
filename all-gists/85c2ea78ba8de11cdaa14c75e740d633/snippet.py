import base64
from Crypto.Cipher import AES
from Crypto import Random

# pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
# unpad = lambda s : s[:-ord(s[len(s)-1:])

KEY = "58897d583d888978b62469889d584472"
PW = "XIANJIAN        "

if __name__ == "__main__":
  # print len(PW)
  d = base64.b64decode(open("flag.txt").read().rstrip())
  c = AES.new(KEY,AES.MODE_ECB,PW)
  print c.decrypt(d)
