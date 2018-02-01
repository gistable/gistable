import httplib2
from lxml import etree
from lxml.etree import ElementTree, Element, SubElement, QName, tostring
cmserver = 'voip-cucm'
cmport = '8443'
location = 'https://' + cmserver + ':' + cmport + '/axl/'
USER = 'axluser'
PASS = 'password'
NS_SOAP_ENV = "{http://schemas.xmlsoap.org/soap/envelope/}"
NS_XSI = "{http://www.w3.org/1999/XMLSchema-instance}"
NS_XSD = "{http://www.w3.org/1999/XMLSchema}"
SOAP_ACTION_NS = "CUCM:DB ver=9.1" 


def SoapRequest(method):
    # create a SOAP request element
    request = Element(method)
    request.set(
        NS_SOAP_ENV + "encodingStyle",
        "http://schemas.xmlsoap.org/soap/encoding/"
        )
    return request

class SoapService:
    def __init__(self, url,username,password):
        self.__client = h = httplib2.Http(".cache",disable_ssl_certificate_validation=True)
        self.__client.add_credentials(username,password)
        self.url = url
    def call(self, action,tree):
        # build SOAP envelope
        envelope = Element(NS_SOAP_ENV + "Envelope")
        body = SubElement(envelope, NS_SOAP_ENV + "Body")
        request = SoapRequest("{http://www.cisco.com/AXL/API/9.1}" + action)
        if type(tree) == list:
            for l in tree:
                request.append(l)
        else:
            request.append(tree)
        body.append(request)
        # call the server
        print tostring(envelope,pretty_print=True)
        resp,resstr = self.__client.request(self.url,"POST",body=tostring(envelope),headers={'SOAPAction':'"CUCM:DB ver=9.1 ' + action + '"'})
        #Convert results back into element
        response = etree.fromstring(resstr)
        return response.find(body.tag)[0]
        #return response




client = SoapService(location,USER,PASS)

name = Element('name')
name.text = "CSFSEVAN"
output = client.call('getPhone',name)
print tostring(output,pretty_print=True)
