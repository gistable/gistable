# Thomas Parslow http://almostobsolete.net
# Just a work in progress and adapted to what I need right now. 
# It does uploads (via a file-like object that you write to) and
# I've started on downloads. Needs the development version of Boto from Github.
#
# Example:
#
#     glacierconn = GlacierConnection(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
#     writer = GlacierWriter(glacierconn, GLACIER_VAULT)
#     writer.write(somedata)
#     writer.write(someotherdata)
#     writer.close()
#     # Get the id of the newly created archive
#     archive_id = writer.get_archive_id()

from boto.connection import AWSAuthConnection
import urllib
import hashlib
import math
import json

class GlacierConnection(AWSAuthConnection):
        
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region="us-east-1",
                 is_secure=True, port=None, proxy=None, proxy_port=None,
                 proxy_user=None, proxy_pass=None,
                 host=None, debug=0, https_connection_factory=None,
                 path='/', provider='aws',  security_token=None,
                 suppress_consec_slashes=True):
        if host is None:
            host = 'glacier.%s.amazonaws.com' % (region,)
        AWSAuthConnection.__init__(self, host,
                aws_access_key_id, aws_secret_access_key,
                is_secure, port, proxy, proxy_port, proxy_user, proxy_pass,
                debug=debug, https_connection_factory=https_connection_factory,
                path=path, provider=provider, security_token=security_token,
                suppress_consec_slashes=suppress_consec_slashes)
        
    def _required_auth_capability(self):
        return ["hmac-v4"]

    def get_vault(self, name):
        return GlacierVault(self, name)

    def make_request(self, method, path, headers=None, data='', host=None,
                     auth_path=None, sender=None, override_num_retries=None):
        headers = headers or {}
        headers.setdefault("x-amz-glacier-version","2012-06-01")
        return super(GlacierConnection, self).make_request(method, path, headers, data, host, auth_path, sender, override_num_retries)
        

class GlacierVault(object):
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def retrieve_archive(self, archive, sns_topic=None, description=None):
        """
        Initiate a archive retrieval job to download the data from an
        archive.
        """
        params = {"Type": "archive-retrieval", "ArchiveId": archive}
        if sns_topic is not None:
            params["SNSTopic"] = sns_topic
        if description is not None:
            params["Description"] = description
        job = GlacierJob(self, params)
        job.initiate()
        return job

    def make_request(self, method, extra_path, headers=None, data=""):
        return self.connection.make_request(method, "/-/vaults/%s%s" % (urllib.quote(self.name),extra_path,), headers, data)

    def get_job(self, job_id):
        return GlacierJob(self, job_id=job_id)


class GlacierJob(object):
    def __init__(self, vault, params=None, job_id=None):
        self.vault = vault
        self.params = params
        self.job_id = job_id

    def initiate(self):
        response = self.vault.make_request("POST", "/jobs", None, json.dumps(self.params))
        
        assert response.status == 202, "Start job expected 202 back (got %s): %r" % (response.status, response.read())
        response.read()
        
        self.job_id = response.getheader("x-amz-job-id")

    def get_output(self, range_from=None, range_to=None):
        headers = {}
        if range_from is not None or range_to is not None:
            assert range_from is not None and range_to is not None, "If you specify one of range_from or range_to you must specify the other"
            headers["Range"] = "bytes %d-%d" % (range_from, range_to)
        response = self.vault.make_request("GET", "/jobs/%s/output" % (urllib.quote(self.job_id),))
        assert response.status == 200, "Get output expects 200 responses (got %s): %r" % (response.status, response.read())
        return response

def chunk_hashes(str):
    """
    Break up the byte-string into 1MB chunks and return sha256 hashes
    for each.
    """
    chunk = 1024*1024
    chunk_count = int(math.ceil(len(str)/float(chunk)))
    chunks = [str[i*chunk:(i+1)*chunk] for i in range(chunk_count)]
    return [hashlib.sha256(x).digest() for x in chunks]

def tree_hash(hashes):
    """
    Given a hash of each 1MB chunk (from chunk_hashes) this will hash
    together adjacent hashes until it ends up with one big one. So a
    tree of hashes.
    """
    while len(hashes) > 1:
        hashes = [hashlib.sha256("".join(h[i:i+1])).digest() for i in range(i,2)]
    return hashes[0]

def bytes_to_hex(str):
    return ''.join( [ "%02x" % ord( x ) for x in str] ).strip()
    
class GlacierWriter(object):
    """
    Presents a file-like object for writing to a Amazon Glacier
    Archive. The data is written using the multi-part upload API.
    """
    DEFAULT_PART_SIZE = 128*1024*1024 #128MB
    def __init__(self, connection, vault, part_size=DEFAULT_PART_SIZE):
        self.part_size = part_size
        self.buffer_size = 0
        self.uploaded_size = 0
        self.buffer = []
        self.vault = vault
        self.tree_hashes = []
        self.archive_location = None
        self.closed = False

        self.connection = connection

        headers = {
                    "x-amz-part-size": str(self.part_size)
                  }
        response = self.connection.make_request(
            "POST",
            "/-/vaults/%s/multipart-uploads" % (urllib.quote(self.vault),),
            headers,
            "")
        assert response.status == 201, "Multipart-start should respond with a 201! (got %s): %r" % (response.status, response.read())
        response.read()
        self.upload_url = response.getheader("location")
        

    def send_part(self):
        buf = "".join(self.buffer)
        # Put back any data remaining over the part size into the
        # buffer
        if len(buf) < self.part_size:
            self.buffer = [buf[self.part_size:]]
            self.buffer_size = len(self.buffer[0])
        else:
            self.buffer = []
            self.buffer_size = 0
        # The part we will send
        part = buf[:self.part_size]
        # Create a request and sign it
        part_tree_hash = tree_hash(chunk_hashes(part))
        self.tree_hashes.append(part_tree_hash)

        headers = {
                    "Content-Range": "bytes %d-%d/*" % (self.uploaded_size, (self.uploaded_size+len(part))-1),
                    "Content-Length": str(len(part)),
                    "Content-Type": "application/octet-stream",
                    "x-amz-sha256-tree-hash": bytes_to_hex(part_tree_hash),
                    "x-amz-content-sha256": hashlib.sha256(part).hexdigest()
                  }

        response = self.connection.make_request(
            "PUT",
            self.upload_url,
            headers,
            part)
        
        assert response.status == 204, "Multipart upload part should respond with a 204! (got %s): %r" % (response.status, response.read())

        response.read()
        
        self.uploaded_size += len(part)
    
    def write(self, str):
        assert not self.closed, "Tried to write to a GlacierWriter that is already closed!"
        self.buffer.append(str)
        self.buffer_size += len(str)
        while self.buffer_size > self.part_size:
            self.send_part()

    def close(self):
        if self.closed:
            return
        if self.buffer_size > 0:
            self.send_part()
        # Complete the multiplart glacier upload
        headers = {
                    "x-amz-sha256-tree-hash": bytes_to_hex(tree_hash(self.tree_hashes)),
                    "x-amz-archive-size": str(self.uploaded_size)
                  }
        response = self.connection.make_request(
            "POST",
            self.upload_url,
            headers,
            "")
        
        assert response.status == 201, "Multipart-complete should respond with a 201! (got %s): %r" % (response.status, response.read())
        response.read()
        self.archive_id = response.getheader("x-amz-archive-id")
        self.closed = True

    def get_archive_id(self):
        self.close()
        return self.archive_id
