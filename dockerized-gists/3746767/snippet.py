class PID(object) :
	def __init__(self, temp_probe, target) :
		self.temp_probe = temp_probe
		self.samples = []
		self.target = target
		GPIO.setup(CHILLPIN, GPIO.OUT)

		self.pid_ts = None
		self.events = []
		GPIO.output(CHILLPIN, False)

		self.fPeriod = 300.0
		self.fMinOff = 60.0 * 3
		assert self.fPeriod > self.fMinOff

		# pid state
		self.fError = None
		self.fIError = 0.0
		self.fDError = None
		self.fPriorError = None

		self.fPID = None

		self.fTemp = None

		# guesstimated PID constants. ratio, not percentage based.
		self.fKP = 0.02
		self.fKI = 0.002
		self.fKD = 0.0