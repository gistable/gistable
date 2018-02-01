import serial

class Lifespan(object):
	def __init__(self):
		self.connect()

	def connect(self):
		self.port = serial.Serial('/dev/tty.IHP-Serialport', 19200, timeout=1)

		while self.port.read(1) != '':
			continue

	def interrogate(self, type):
		self.port.write(''.join(map(chr, (161, type, 0, 0, 0))))
		return tuple(map(ord, self.port.read(6))[2:])

	@property
	def seconds(self):
		msg = self.interrogate(137)
		return msg[0] * 60 * 60 + msg[1] * 60 + msg[2]

	@property
	def time(self):
		msg = self.interrogate(137)
		return msg[0:3]

	@property
	def distance(self):
		msg = self.interrogate(133)
		return msg[0] + msg[1] / 100.0

	@property
	def speed(self):
		msg = self.interrogate(130)
		return msg[0] + msg[1] / 100.0

	@property
	def calories(self):
		msg = self.interrogate(135)
		return msg[0] * 256 + msg[1]

	@property
	def steps(self):
		msg = self.interrogate(136)
		return msg[0] * 256 + msg[1]

lifespan = Lifespan()
while True:
	print 'Walking for: %i:%i:%i' % lifespan.time
	print 'Walked %f miles (currently %f mph)' % (lifespan.distance, lifespan.speed)
	print 'Burned %i calories in %i steps' % (lifespan.calories, lifespan.steps)
	print
