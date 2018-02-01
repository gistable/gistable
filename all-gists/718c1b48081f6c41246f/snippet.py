##A palindromic number reads the same both ways. The largest palindrome made from the product of two 2-digit numbers is 9009 = 91 * 99.
##Find the largest palindrome made from the product of two 3-digit numbers.

nDigs = 3

hilim = nDigs*'9'
lolim = (nDigs - 1)*'9'

ihi = int(hilim)
ilo = int(lolim)

from datetime import datetime

print('Palindromic number search for N =',nDigs)

#============================================

tstart = datetime.now()

fnd_v1 = 0
fnd_v2 = 0
fnd_xx = 0

pwr = 10 ** nDigs

fmt1 = '{:0'
fmt2 = 'd}'
fmtx = fmt1 + str(nDigs) + fmt2

for v1 in range(ihi,ihi//2,-1):
	if v1*ihi < fnd_xx:
		break
	for v2 in range(ihi,ilo,-1):
		v1v2 = v1 * v2
		if v1v2 <= fnd_xx:
			break
		parts = divmod(v1v2,pwr)
		shi = fmtx.format(parts[0])
		slo = fmtx.format(parts[1])
		if (shi == slo[::-1]):
			fnd_v1 = v1
			fnd_v2 = v2
			fnd_xx = v1v2
			
tend = datetime.now()
print(tend - tstart)

print('found:',fnd_v1,'x',fnd_v2,'=',fnd_xx)

#============================================

tstart = datetime.now()

fnd_v1 = 0
fnd_v2 = 0
fnd_xx = 0

for v1 in range(ihi,ihi//2,-1):
	if v1*ihi < fnd_xx:
		break
	for v2 in range(ihi,ilo,-1):
		v1v2 = v1 * v2
		if v1v2 <= fnd_xx:
			break
		sxx = str(v1v2)
		shi = sxx[:len(sxx)//2]
		slo = sxx[:len(sxx)//2-1:-1]
		if (shi == slo):
			fnd_v1 = v1
			fnd_v2 = v2
			fnd_xx = v1v2

tend = datetime.now()
print(tend - tstart)

print('found:',fnd_v1,'x',fnd_v2,'=',fnd_xx)

#============================================

def GetNumLen(number):
	n1 = number
	pwr = 0
	while n1 > 0:
		n1 = n1 // 10
		pwr += 1
		#print(n1,pwr)
	return pwr

def GetNumPos(number,position):
	n1 = number // 10**position
	return n1 % 10

def RevNumber(number):
	m = 0
	pwr = GetNumLen(number)
	for i in range(pwr):
		ni = GetNumPos(number,pwr-i-1)
		m += ni*10**i
		#print(i,ni,m)
	return m

tstart = datetime.now()

fnd_v1 = 0
fnd_v2 = 0
fnd_xx = 0

for v1 in range(ihi,ihi//2,-1):
	if v1*ihi < fnd_xx:
		break
	for v2 in range(ihi,ilo,-1):
		v1v2 = v1 * v2
		if v1v2 <= fnd_xx:
			break
		v2v1 = RevNumber(v1v2)
		if (v1v2 == v2v1):
			fnd_v1 = v1
			fnd_v2 = v2
			fnd_xx = v1v2

tend = datetime.now()
print(tend - tstart)

print('found:',fnd_v1,'x',fnd_v2,'=',fnd_xx)

#============================================
