
import hashlib   #for converting passwords and guesses to hashes
import time      #for timing the program and counting the passwords/ second

#variables

password = ''
passwordHash = ''

timeOld = time.time()
startTime = time.time()
timeNow = time.time()
pws = 0
pwscounter = 0

guess = ''

error = False
loops = 0

chars = '1234567890abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZZ'
charslen = len(chars)

answer = ''

cracked = False

i, i2, i3, i4, i5, i6, i7, i8, i9, i10 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

c, c2, c3, c4, c5, c6, c7, c8, c9, c10 = '', '', '', '', '', '', '', '', '', ''

#functions

def clear():
    print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'

#program start
#mode selection


print 'Please enter the SHA-1 hash you wish to crack.'
passwordHash = raw_input('>')
print passwordHash
clear()
print 'starting...'
startTime = time.time()    #where the timer starts, and the beginning of the cracking loops
while cracked == False:
	while i <= charslen-1:
		while i2 <= charslen-1:
			while i3 <= charslen-1:
				while i4 <= charslen-1:
					while i5 <= charslen-1:
						while i6 <= charslen-1:
							while i7 <= charslen-1:
								while i8 <= charslen-1:
									while i9 <= charslen-1:
										while i10 <= charslen-1:
										        timeNow = time.time()         #area of main cracking calculations
										        if timeNow - timeOld >= 1:
										            pws = pwscounter
										            pwscounter = 0
										            timeOld = time.time()
											c10 = chars[i10]
											guess = c
											guess += c2
											guess += c3
											guess += c4
											guess += c5
											guess += c6
											guess += c7
											guess += c8
											guess += c9
											guess += c10
											loops += 1
											hashed = hashlib.sha1(guess).hexdigest()
											if hashed[0:6] == passwordHash:
												cracked = True
												break
											if loops >= charslen**10:
												cracked = True
												error = True
												break
										        pwscounter += 1
											i10 += 1
										c9 = chars[i9]
										i9 += 1
										i10 = 0
										if cracked == True:
											break
									c8 = chars[i8]
									i8 += 1
									i9 = 0
									if cracked == True:
										break
								c7 = chars [i7]       #print statistics on progress, and passwords/ minute
								i7 += 1
								i8 = 0
								print passwordHash
								print hashed
								print guess
								print 'pw/s:', pws
								print 'guesses:', loops
								print '\n'
								if cracked == True:
									break
							c6 = chars [i6]
							i6 += 1
							i7 = 0
							if cracked == True:
								break
						c5 = chars [i5]
						i5 += 1
						i6 = 0
						if cracked == True:
							break
					c4 = chars [i4]
					i4 += 1
					i5 = 0
					if cracked == True:
						break
				c3 = chars[i3]
				i3 += 1
				i4 = 0
				if cracked == True:
					break
			c2 = chars [i2]
			i2 += 1
			i3 = 0
			if cracked == True:
				break
		c = chars [i]
		i += 1
		i2 = 0
		if cracked == True:
			break

            #return the result

if error == False:
	print 'Cracked!'
	print 'The password is:', guess
	print 'Tried', loops, 'combinations in', round(timeNow-startTime, 2),'seconds'
        if timeNow == startTime:
            timeNow += 1
	print 'An average of', round(loops/(timeNow-startTime),2),'pw/s'
else:
	print 'Unable to crack password, please make sure the hash is in SHA-1.'
	print 'If the hash is in SHA-1, then the password is either longer than 10 characters, or contains a character that is not specified.'
