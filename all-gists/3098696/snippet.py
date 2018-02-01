import time
from   retro import *
class Timeout(Component):
	@on(GET="{_:rest}")
	def timeout( self, request, _ ):
		time.sleep(20)
		return request.respond("OK!")
run(Application(Timeout()))
# EOF