# Crack Xerox Alto disk passwords using math.

def findPasswd(passvec):
  # a and b are the salt values
  a = (passvec[1] << 16) + passvec[2]
  b = (passvec[3] << 16) + passvec[4]

  # c is the known hashed password
  # The password characters are concatenated into x and y.

  # Since we don't know the password, brute force the 65536 possibilities for x
  c = (passvec[5] << 48) | (passvec[6] << 32) | (passvec[7] << 16) | passvec[8];
  for x in range(0, 65536):

    # Solve the password equation for y
    t = (x * x) & 0xffffffff
    t = (t * a) & 0xffffffffffffffff
    t ^= 0xffffffff00000000
    t += 1
    btimesy = (c - t) & 0xffffffffffffffff
    y = btimesy / b

    # If quotient didn't work, try next x
    if (y * b) & 0xffffffffffffffff != btimesy: continue

    # Concat sequence is first char into x, next two into y, one into x, etc.
    # Try different password lengths to find which one works
    for i in range(1, 15):
      password = ''
      x1 = x
      y1 = y
      for j in range(i, 0, -1):
        if (j % 3) == 1:
	  char = chr((x1 >> 9) & 0x7f)
	  x1 = (x1 << 7) & 0xffff
	else:
	  char = chr((y1 >> 25) & 0x7f)
	  y1 = (y1 << 7) & 0xffffffff
	password = char + password
      if x1 == 0 and y1 == 0 and '\0' not in password:
        print i, password
        

# Crack passwords from three Alto disks
def main():
  print 'Disk 37'
  # passvec is the 9-word password vector from sys.boot
  # passvec must be big-endian
  passvec = [0xffff, 0xe9d3, 0x0f9a, 0x0da5, 0x53b4, 0xc3f4, 0x382a, 0xd974, 0x5589]
  findPasswd(passvec)

  print '\nDisk 47'
  passvec = [0xffff, 0xcfa7, 0x9f3d, 0x669a, 0xf2bb, 0xf193, 0x6d09, 0x4571, 0xe1d1]
  findPasswd(passvec)

  print '\nDisk 72'
  passvec = [0xffff, 0x8341, 0x772c, 0x249b, 0x1be2, 0xf71f, 0x5b87, 0x9fce, 0x0581]
  findPasswd(passvec)

if __name__ == "__main__":
    main()
