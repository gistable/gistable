#!/usr/bin/python

################################################################################

'''Command line tool to build PassKit .pkpass files'''

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
import zipfile

import envoy # pip install --user envoy
import docopt # pip install --user envoy

################################################################################

class PassKit(object):

    def __init__(self):
        pass

    ############################################################################

    def convert_certificate(self, input = None, output = None):

        assert os.path.isfile(input)
        assert os.path.splitext(input)[1] == '.p12'
        
        if not output:
            output = os.path.splitext(input)[0] + '.pem'

        subprocess.call(["openssl", "pkcs12", "-clcerts", "-nokeys", "-in", input, "-out", output])

    ############################################################################

    def convertKey(self, input = None, output = None, removePassword = True):

        assert os.path.isfile(input)
        assert os.path.splitext(input)[1] == '.p12'
        
        if not output:
            output = os.path.splitext(input)[0] + '.pem'

        subprocess.call(["openssl", "pkcs12", "-nocerts", "-nokeys", "-in", input, "-out", output])

        if removePassword:
            subprocess.call(["openssl", "rsa", "-in", input, "-out", output])

    ############################################################################

    def sign(self, certificate, key, input, output):

        subprocess.call(['openssl', 'smime', '-binary', '-sign', '-signer', certificate, '-inkey', key, '-in', input, '-out', output, '-outform', 'DER'])

    ############################################################################

    def validate(self, directory):
        return True

    ############################################################################

    # TODO - does not work with nested directories (e.g. localizations) yet.

    def manifest(self, directory):
        theFiles = os.listdir(directory)
        
        theFiles = (f for f in theFiles if f not in ('.DS_Store', 'signature', 'manifest.json'))
        theFiles = (f for f in theFiles if f[0] != '.')
        theFiles = (f for f in theFiles if os.path.isfile(os.path.join(directory, f)))
        
        theManifest = dict(((f, hashlib.sha1(file(os.path.join(directory, f)).read()).hexdigest()) for f in theFiles))

        return theManifest

    ############################################################################

    # TODO - does not work with nested directories (e.g. localizations) yet.

    def archive(self, directory, output):
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as myzip:
            for f in os.listdir(directory):
                myzip.write(os.path.join(directory, f), f)

    ############################################################################

    def build(self, key = None, output = None, template = None, certificate = None):

        assert os.path.isdir(template)
        assert os.path.isfile(certificate)
        assert os.path.isfile(key)

        ########################################################################

        theTempDirectory = tempfile.mkdtemp()
        theTempDirectory = os.path.join(theTempDirectory, 'template')
        shutil.copytree(template, theTempDirectory)
        
        scratch = theTempDirectory
    
        ########################################################################
        
        thePassPath = os.path.join(scratch, 'pass.json')
        thePass = json.load(file(thePassPath))
        
        thePass['serialNumber'] = uuid.uuid4().urn
        
        json.dump(thePass, file(thePassPath, 'w'), sort_keys=True, indent=4)
        
        ########################################################################
        
        theManifest = self.manifest(scratch)
        
        theManifestPath = os.path.join(scratch, 'manifest.json')
        json.dump(theManifest, file(theManifestPath, 'w'), sort_keys=True, indent=4)
        
        ########################################################################

        self.sign(key = key, certificate = certificate, input = os.path.join(scratch, 'manifest.json'), output = os.path.join(scratch, 'signature'))
                
        ########################################################################

        if not self.validate(scratch):
            raise Exception('Could not validate')

        ########################################################################
        
        self.archive(scratch, output)
    
################################################################################

if __name__ == '__main__':
    __doc__ = """passkit. Tool for building PassKit .pkpass files
Usage:
  passkit build --output=OUTPUT --template=TEMPLATE --certificate=CERTIFICATE --key=KEY
  passkit convert_certificate --input=INPUT --output=OUTPUT
  passkit convert_key --input=INPUT --output=OUTPUT [--remove_password]
  passkit help | -h | --help
  passkit -v | --version

Options:
-i INPUT, --input=INPUT                     Path to input file/directory
-o OUTPUT, --output=OUTPUT                  Path to output file/directory
-t TEMPLATE, --template=TEMPLATE            Path to template pass directory.
-c CERTIFICATE, --certificate=CERTIFICATE   Path to certificate file (.pem)
-k KEY, --key=KEY                           Path to key file (.pem)
--remove_password                           Remove password from output key pem file
"""

    arguments = docopt.docopt(__doc__, version='passkit 0.1')
#     print arguments
    if 'build' in arguments and arguments['build']:
        theKit = PassKit()
        theKit.build(
            key = arguments['--key'],
            output = arguments['--output'],
            template = arguments['--template'],
            certificate = arguments['--certificate']
            )        
        
    elif 'convert_certificate' in arguments and arguments['convert_certificate']:
        theKit = PassKit()
        theKit.convert_certificate(
            input = arguments['--input'],
            output = arguments['--output']
            )
