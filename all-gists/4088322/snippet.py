"""
SUDS caches WSDL files by default.  This command will clear the cache. 
"""

from openkm import client
client = client.Client(url)
client.options.cache.clear()