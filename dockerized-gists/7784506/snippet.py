import logging

from suds.xsd.doctor import ImportDoctor, Import
from suds.client import Client, WebFault

logger = logging.getLogger(__name__)


wsdl_url = 'http://appls-srv.araskargo.com.tr/arascargoservice/arascargoservice.asmx?WSDL'
client = None
data = {}

imp = Import("http://www.w3.org/2001/XMLSchema")

# Add namespaces. Find in wsdl
imp.filter.add('http://tempuri.org/IrsaliyeData.xsd')
imp.filter.add('http://tempuri.org/WebCargoData.xsd')
doctor = ImportDoctor(imp)

try:
    client = Client(wsdl_url, doctor=doctor)
except WebFault as e:
    logger.debug(e)
    raise e

data['CargoKey'] = 'abc123'
# Fill required data. Look at wsdl for required data

try:
    # Look at wsdl_url for more parameters etc.
    # SetDispatch is a remote method. Calling over soap. 
    # Look at print(client) for which methods exists.

    response = client.service.SetDispatch(
        {'ShippingOrder': data},
        userName="abc",
        password="123"
    )

    logger.debug(response)

except WebFault as e:
    logger.error("SetDispatch Error: %s" % e)
    raise e
