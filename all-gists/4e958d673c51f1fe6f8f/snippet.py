import itertools

from PIL import Image

#def mandel(z, c):
#	return z ** 2 + c
	
result = Image.new("L", (400, 400))

for r, i in itertools.product(xrange(400), repeat=2):
	c = complex(r / 100.0 - 2.0, i / 100.0 - 2.0)
	z = 0
	print c
	result.putpixel((r, i), 255)
	for cnt in xrange(50):
		z = z ** 2 + c
		if not (-2 < z.real < 2) or not (-2 < z.imag < 2):
			result.putpixel((r, i), int(cnt * 5.12))
			break

result.save('mandel.png')
