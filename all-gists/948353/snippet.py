N = 1001
def collatz_sequences(n):
	while n > 1:
		print n
		if (n % 2) != 0:
			n = (3 * n) + 1
		else:
			n = n / 2
	print n

if __name__ == '__main__':
    collatz_sequences(N)