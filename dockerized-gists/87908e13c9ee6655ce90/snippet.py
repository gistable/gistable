import sys

from suds import client
from suds.wsse import Security, UsernameToken
from suds.sax.text import Raw
from suds.sudsobject import asdict
from suds import WebFault

'''
Given a Workday Employee_ID, returns the last name of that employee.

I had trouble finding working examples online of interacting with the Workday SOAP API
via Python - both the authentication piece and data retrieval. It turns out to be very simple,
but it took a while to come up with due to scant documentation, so posting here in case
anyone finds it helpful.

The most common SOAP lib for Python is suds, but suds has fallen out of maintenance as
SOAP has fallen out of favor over the past 5-10 years.
suds is officially replaced by suds-jurko, which is now part of Fedora:

https://bitbucket.org/jurko/suds
https://fedorahosted.org/suds/wiki/Documentation

pip install suds-jurko
'''

# Uncomment for full debug output:
# import logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
# logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

# Fully credentialed service user with access to the Human Resources API
username = 'username@yourtenant'
password = 'xxxxxxxxxxxxxxxxxx'

wsdl_url = 'https://wd5-impl-services1.workday.com/ccx/service/[yourtenant]/Human_Resources/v24.1?wsdl'
Employee_ID = '123456'  # Replace with a known user ID in your tenant
client = client.Client(wsdl_url)

# Wrapping our client call in Security() like this results in submitting
# the auth request with PasswordType in headers in the format WD expects.
security = Security()
token = UsernameToken(username, password)
security.tokens.append(token)
client.set_options(wsse=security)

# The workflow is, generate an XML element containing the employee ID, then post
# that element to the Get_Workers() method in the WSDL as an argument.
# We could do this with two suds calls, having it generate the XML from the schema,
# but here I'm creating the POST XML manually and submitting it via suds's `Raw()` function.
xmlstring = '''
<ns0:Worker_Reference>
    <ns0:ID ns0:type="Employee_ID">{id}</ns0:ID>
</ns0:Worker_Reference>
'''.format(id=Employee_ID)

xml = Raw(xmlstring)

try:
    result = client.service.Get_Workers(xml)
except WebFault as e:
    # Employee ID probably doesn't exist.
    print(e)
    sys.exit()

# ===================
# That's essentially all you need. Everything below is just response parsing.
# ===================


# Converts the unusually formatted response object to standard Python dictionary.
# You'll probably want to move this into a utils.py and import it.
def recursive_asdict(d):
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out

worker_dict = recursive_asdict(result)
worker = worker_dict['Response_Data']['Worker'][0]['Worker_Data']
lname = worker['Personal_Data']['Name_Data']['Legal_Name_Data']['Name_Detail_Data']['Last_Name']

print(lname)
