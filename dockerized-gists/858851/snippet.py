from suds.client import Client
from suds.bindings import binding
import logging


USERNAME = 'username'
PASSWORD = 'password'

# Just for debugging purposes.
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

# Telnic's SOAP server expects a SOAP 1.2 envelope, not a SOAP 1.1 envelope
# and will complain if this hack isn't done.
binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
client = Client('client.wsdl',
		username=USERNAME,
		password=PASSWORD,
		headers={'Content-Type': 'application/soap+xml'})

# This will now work just fine.
client.service.someRandomMethod()