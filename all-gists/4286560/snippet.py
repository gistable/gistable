def RGB2YUV(input):
  (R, G, B) = input
	Y = int(0.299 * R + 0.587 * G + 0.114 * B)
	U = int(-0.147 * R + -0.289 * G + 0.436 * B)
	V = int(0.615 * R + -0.515 * G + -0.100 * B)
	
	return (Y, U, V)

def YUV2RGB(input):
	(Y, U, V) = input
	R = int(Y + 1.14 * V)
	G = int(Y - 0.39 * U - 0.58 * V)
	B = int(Y + 2.03 * U)
	
	return (R, G, B)

print YUV2RGB((73,186,154))