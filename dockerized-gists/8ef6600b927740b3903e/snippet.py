import os
import os.path
import tempfile

from subprocess import Popen, PIPE

class MiniAFSK(object):
	def __init__(self, data_rate=1200, frequency=27.5):
		self.data_rate = data_rate
		self.frequency = frequency
		# minimodem wants the file name to end in .flac
		self.fifo_path = os.path.join(tempfile.gettempdir(), "afskfifo.flac")
		if not os.path.exists(self.fifo_path):
			os.mkfifo(self.fifo_path)

	def send(self, data):
		modem = Popen(["minimodem", "-q", "--tx", str(self.data_rate), "-f", self.fifo_path], stdin=PIPE)
		sox = Popen(["sox", "-tflac", self.fifo_path, "-esigned-integer", "-b16", "-c1", "-r48000", "-traw", "-"], stdout=PIPE)
		pifm = Popen(["pifm", "-", str(self.frequency), "48000"], stdin=sox.stdout)
		modem.communicate(data)

		if modem.poll():
			modem.kill()

		if sox.poll():
			sox.kill()

		if pifm.poll():
			pifm.kill()

if __name__ == "__main__":
	print "Testing the transmitter"
	print "Frequency: 27.5MHz, Data rate: 1200"
	print "Type \"y\" to proceed"
	if raw_input().lower() == "y":
		print "Testing..."
		afsk = MiniAFSK()
		print "Send..."
		afsk.send("Hello, World!"*16)
	print "Exiting"
