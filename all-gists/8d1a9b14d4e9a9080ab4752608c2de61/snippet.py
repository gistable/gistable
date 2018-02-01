#!/usr/bin/env python
###############################################################################
# This script uploads a file to an AWS S3 bucket.  It will optionally use KMS
# envelope encryption to encrypt a file on the client side before uploading
# to AWS S3.
#
# Envelope encryption fetches a data key from KMS and uses it to encrypt the
# file.  The encrypted file is uploaded to an S3 bucket along with an encrypted
# version of the data key (it's encrypted with a KMS master key).  You must
# have access to the KMS master key to decrypt the data key and file.
#
# The input file is read in parts.  Each part is then encrypted (optional)
# with a KMS data key and multipart uploaded to an S3 bucket using a different
# thread.  Processing by part allows large files to be encrypted/uploaded
# without requiring large amounts of memory, and threading improves performance
# by uploading multiple parts in parallel.
#
# Usage:
#   s3_put -p aws_profile -f input_file -b s3_bucket -s s3_key [-k kms_key]
#          [-c part_size] [-m metadata] [-t threads] [-i] [-d debug_level]
#
# Parameter descriptions:
#   aws_profile: name of your AWS profile
#   input_file:  input file name
#   s3_bucket:   name of the S3 bucket where your object will be uploaded
#   s3_key:      key (path/name) of the S3 object to be uploaded
#   kms_key:     ARN/alias of the AWS KMS key used to encrypt your data key.
#                Default is to not encrypt
#   part_size:   size of parts, in bytes, to be processed, with each part
#                being encrypted and uploaded (multipart) to S3.  Default is
#                40MB (41943040 bytes).
#   metadata:    a optional list of values, in JSON format, that will be
#                attached to the S3 object.
#   threads:     number of threads used to upload file parts to S3
#   -i:          by default, object metadata is attached to the S3 object.  If
#                this switch is given, then metadata will be written, in json
#                format, to a ".instruction" S3 object in the same bucket with
#                the same key name appended with ".instruction".  See the code
#                below for metadata key/value content.
#   debug_level: default is INFO
#
# Examples:
#   s3_put.py -p GR_GG_COF_AWS_Techops_Dev_Developer
#     -f local_file.dat -b s3_bucket_name -s s3_key_name
#     -k arn:aws:kms:us-east-1:076173845600:key/064fd0a4-50c1-4385-af8e-ff207950fcad
#     -m '{"user": "abc123", "group": "samuser", "permissions": "644"}'
#
#   s3_put.py -p GR_GG_COF_AWS_Techops_Dev_Developer
#     -f local_file.dat -b s3_bucket_name -s s3_key_name
#     -k alias/cof/s3/encrypted
#     -m '{"user": "abc123", "group": "samuser", "permissions": "644"}'
###############################################################################

from __future__ import print_function
import os
import sys
import argparse
import logging
import math
import time as t
import datetime as dt
import base64
import json
import threading
import gc
import traceback
import ast
import boto3
from botocore.client import Config
from Crypto import Random
from Crypto.Cipher import AES

def pad_pkcs7(s):
    ''' PKCS7 adds bytes with each having the value of the padding length '''
    pad_len = AES.block_size - (len(s) % AES.block_size)
    return s + pad_len * chr(pad_len)

def unpad_pkcs7(s):
    return s[0:-ord(s[-1])]

def current_ts():
    return int((dt.datetime.utcnow().replace(microsecond=0) -
                dt.datetime(1970,1,1).replace(microsecond=0)).total_seconds())

def kms_encryption_setup(session, kms_key):
    ''' Get the KMS key from AWS and initialize the cipher object '''
    kms = session.client('kms')

    # Convert arn into alias.
    if kms_key[:4] == "arn:":
        try:
            kms_key_list = kms.list_keys()['Keys']
            kms_alias_list = kms.list_aliases()['Aliases']
            kms_key_id = [k['KeyId'] for k in kms_key_list
                          if k['KeyArn'] == kms_key][0]
            kms_key_alias = [a['AliasName'] for a in kms_alias_list
                             if a.get('TargetKeyId') == kms_key_id][0]
            logging.info("kms key alias: %s", kms_key_alias)
            kms_key = kms_key_alias
        except:
            # Ignore all errors; use the arn for the key
            pass

    # Get data key from KMS and create the cipher object.
    logging.info("Getting data key from AWS KMS...")
    encryption_context = {"kms_cmk_id": kms_key}
    data_key = kms.generate_data_key(KeyId=kms_key, KeySpec='AES_256',
                                     EncryptionContext=encryption_context)
    iv = Random.new().read(AES.block_size)
    aes_cipher = AES.new(data_key['Plaintext'], mode=AES.MODE_CBC, IV=iv)

    # Create metadata that includes the encryption context, encrypted data
    # key, cipher method/mode/padding, and initialization vector.  Metadata
    # key names match those used by the AWS Java API; using them allows us
    # to download and decrypt using the AWS Java API.
    metadata = {
        'x-amz-wrap-alg': 'kms',
        'x-amz-matdesc': json.dumps(encryption_context),
        'x-amz-key-v2': base64.b64encode(data_key['CiphertextBlob']),
        'x-amz-cek-alg': 'AES/CBC/PKCS5Padding',
        'x-amz-iv': base64.b64encode(iv)
    }

    return aes_cipher, metadata


def main():
    class Parts(object):
        ''' Upload an S3 object in multiple parts, each in a different
            thread.  Encrypts if requested.
        '''
        def __init__(self):
            self.num_s3_parts = num_s3_parts
            self.max_running = args.threads
            logging.info("S3 object parts: %d" % self.num_s3_parts)
            logging.debug("Max running threads: %d" % self.max_running)
            self.parts = ['0-index not used']  #S3 part numbers are 1-relative
            self.total_size_uploaded = 0
            self.total_upload_secs = 0
            self.max_upload_secs = 0

        def num_parts(self):
            return len(self.parts) - 1

        def num_running(self):
            return len([p for p in self.parts[1:] if p['status'] == 'RUNNING'])

        def num_uploaded(self):
            return len([p for p in self.parts[1:]
                       if p['status'] in ['UPLOADED','COMPLETED']])

        def num_completed(self):
            return len([p for p in self.parts[1:] if p['status'] == 'COMPLETED'])

        def num_failed(self):
            return len([p for p in self.parts[1:] if p['status'] == 'FAILED'])

        def upload_part(self, part_num):
            ''' Upload a specific part of the S3 object '''
            try:
                logging.debug("Starting thread %d" % part_num)
                before_upload = current_ts()
                resp = s3.upload_part(Body=self.parts[part_num]['data'],
                                      Bucket=args.bucket, Key=args.s3_key,
                                      PartNumber=part_num,
                                      UploadId=mpu['UploadId'])
                self.parts[part_num]['time'] = current_ts() - before_upload
                self.parts[part_num]['mpu_part'] = {'ETag': resp['ETag'],
                                                    'PartNumber': part_num}
                self.parts[part_num]['status'] = 'UPLOADED'
                logging.debug("Ending thread %d, size %d" %
                              (part_num, self.parts[part_num]['size']))
            except Exception as e:
                self.parts[part_num]['status'] = 'FAILED'
                logging.error("Thread %d failed" % part_num)
                traceback.print_exc()

        def read_part(self, part_num):
            ''' Read a part from the file and encrypt '''
            logging.debug("Reading part %d" % part_num)
            readbuf = fin.read(part_size)
            if aes_cipher:
                if part_num == self.num_s3_parts:
                    # Last part must be padded
                    logging.debug("Padding part %d" % part_num)
                    readbuf = pad_pkcs7(readbuf)
                logging.debug("Encrypting part %d" % part_num)
                readbuf = aes_cipher.encrypt(readbuf)
            return readbuf

        def start_thread(self):
            ''' Start a new thread to upload a part of the S3 object '''
            part_num = len(self.parts)
            readbuf = self.read_part(part_num)
            new_thread = threading.Thread(name="Thread"+str(part_num),
                                          target=self.upload_part,
                                          args=(part_num,))
            self.parts.append({'thread':new_thread,
                               'time':0,
                               'data':readbuf,
                               'size':len(readbuf),
                               'mpu_part':None,
                               'status':'RUNNING'})
            new_thread.start()

        def collect_thread(self):
            ''' Mark each part COMPLETED after it has been uploaded.  Garbage
                collect to prevent large amount of memory usage when the file
                is large.
            '''
            part_num = self.num_completed()+1
            if (self.num_parts() >= part_num and
                self.parts[part_num]['status'] == 'UPLOADED'
               ):
                part = self.parts[part_num]
                logging.debug("Uploaded part %d in %d seconds" % (
                              part_num, part['time']))
                self.max_upload_secs = (
                    part['time'] if part['time'] > self.max_upload_secs
                    else self.max_upload_secs)
                self.total_upload_secs += part['time']
                self.total_size_uploaded += part['size']
                part['status'] = 'COMPLETED'
                part['data'] = None
                gc.collect()  # Clean-up unreferenced data.
                return True
            else:
                return False

        def encrypt_and_upload(self):
            ''' Manages threads used to read each part of the file, encrypt,
                and upload to the S3 object.
            '''
            # Loop until any child thread fails or all parts have been
            # uploaded.
            while (self.num_failed() == 0 and
                   self.num_completed() < self.num_s3_parts):
                # Start a new thread if...
                #  1) We're running fewer than the max allowed
                #  2) There are still more parts to process
                if (self.num_running() < self.max_running and
                    self.num_parts() < self.num_s3_parts
                   ):
                    self.start_thread()
                    # If the number of parts completed is less than the number
                    # of parts uploaded - 300, then collect a thread.  This is
                    # important, because sometimes threads will finish faster
                    # than new threads can start (seems like that shouldn't
                    # happen, but it can) and without this step we'll never
                    # run the max number of threads and no threads will be
                    # collected until all have finished.  That's okay for small
                    # files, but not for very large files because the memory
                    # for each part isn't released until the thread has been
                    # collected and not releasing memory will cause problems
                    # when the file is extremely large.
                    if self.num_completed() < self.num_uploaded() - 300:
                        self.collect_thread()
                elif not self.collect_thread():
                    # Sleep if a thread was not started nor collected.
                    t.sleep(5)
                logging.info("parts: total %d, started %d, running %d, "
                             "uploaded %d, completed %d" %
                             (self.num_s3_parts, self.num_parts(),
                              self.num_running(), self.num_uploaded(),
                              self.num_completed()))

            fin.close()
            if self.num_failed() == 0:
                logging.info("All parts uploaded: total_size_uploaded %d, "
                    "max_upload_secs %d, avg_upload_secs %d" % (
                    self.total_size_uploaded, self.max_upload_secs,
                    int(self.total_upload_secs/self.num_s3_parts)))
            return self.num_failed()

    # Get arguments
    aparser = argparse.ArgumentParser()
    aparser.add_argument("-p", "--profile", required=True, help="AWS profile")
    aparser.add_argument("-f", "--file", required=True,
        help="name of file to be encrypted and uploaded to S3")
    aparser.add_argument("-b", "--bucket", required=True, help="S3 bucket")
    aparser.add_argument("-s", "--s3_key", required=True, help="S3 key")
    aparser.add_argument("-k", "--kms_key",
        help="arn or alias of the KMS customer master key")
    aparser.add_argument("-c", "--part_size", default="41943040",
        help="size of each part to be uploaded (default is 40MB)")
    aparser.add_argument("-m", "--metadata", default="{}",
        help="a list of values, in JSON format, that will be attached to the S3 object")
    aparser.add_argument("-t", "--threads", type=int, default=5,
        help="number of threads for parallel upload")
    aparser.add_argument("-i", "--instruction", action="store_true",
        help="store metadata in a .instruction S3 object (default is to attach metadata to the S3 object")
    aparser.add_argument("-d", "--debug_level", default="INFO",
        help="debug level (default is INFO)")
    args = aparser.parse_args()

    # Configure logging
    cformat = "%(threadName)s:%(asctime)s:%(levelname)s:%(message)s"
    cdatefmt = "%Y-%m-%dT%H:%M:%SZ"
    logging.Formatter.converter = t.gmtime
    logging.basicConfig(format=cformat, datefmt=cdatefmt, stream=sys.stdout,
                        level=args.debug_level)
    #logging.getLogger("boto3").setLevel(logging.INFO)
    #logging.getLogger("botocore").setLevel(logging.INFO)

    if not (os.environ.get('http_proxy') and os.environ.get('https_proxy')):
        logging.error("http_proxy and https_proxy must be set")
        sys.exit(1)

    logging.info("profile: %s", args.profile)
    logging.info("file: %s", args.file)
    logging.info("bucket: %s", args.bucket)
    logging.info("s3_key: %s", args.s3_key)
    logging.info("kms_key: %s", args.kms_key)
    logging.info("metadata: %s", args.metadata)
    args.threads = min(10, args.threads)   # max 10 threads
    logging.info("threads: %s", args.threads)
    logging.info("instruction: %s", args.instruction)

    # part_size must be a multiple of AES.block_size
    part_size = int(args.part_size)
    if part_size % AES.block_size != 0:
        part_size += AES.block_size - (part_size % AES.block_size)
    logging.info("part_size: %s", part_size)

    # Determine number of file parts.
    st_size = os.stat(args.file).st_size
    if st_size == 0:
        logging.error("Source data is 0 bytes, nothing uploaded to S3")
        sys.exit(2)
    logging.info("file size: %d" % st_size)
    num_s3_parts = math.ceil(float(st_size) / part_size)

    # Create AWS session for the given profile.
    session = boto3.Session(profile_name=args.profile)
    s3 = session.client('s3', config=Config(signature_version='s3v4',
                                            read_timeout=300))

    # If user provided a KMS key, then setup the encryption stuff.
    if args.kms_key:
        aes_cipher, metadata = kms_encryption_setup(session, args.kms_key)
        logging.info("Data will be encrypted before loading to S3")
    else:
        aes_cipher, metadata = None, {}
        logging.info("Data will not be encrypted before loading to S3")
    metadata.update(ast.literal_eval(args.metadata))

    # Load the file to S3 in parts.
    # Metadata will either be attached to the S3 object or stored in an
    # accompanying .instruction S3 object.
    # Also using Server Side Encryption because it's required in our AWS
    # environment.
    if args.instruction:
        mpu = s3.create_multipart_upload(Bucket=args.bucket, Key=args.s3_key,
              ServerSideEncryption='AES256')
    else:
        mpu = s3.create_multipart_upload(Bucket=args.bucket, Key=args.s3_key,
              Metadata=metadata, ServerSideEncryption='AES256')

    # Initiate the process to encrypt and upload to an S3 object.
    logging.info("Uploading parts of data to s3://%s/%s..." %
                 (args.bucket, args.s3_key))
    fin = open(args.file, "rb")
    parts = Parts()
    if parts.encrypt_and_upload() != 0:
        sys.exit(5)
    else:
        # Complete the multipart upload.
        # Create a metadata S3 object if requested.
        logging.info("Completing multi-part upload")
        parts_list = [p['mpu_part'] for p in parts.parts[1:]]
        s3.complete_multipart_upload(Bucket=args.bucket, Key=args.s3_key,
                                     MultipartUpload={'Parts': parts_list},
                                     UploadId=mpu['UploadId'])
        if args.instruction:
            logging.info("Creating .instruction S3 object")
            if aes_cipher:
                s3.put_object(Bucket=args.bucket,
                    Key=args.s3_key+'.instruction',
                    Body=json.dumps(metadata),
                    ServerSideEncryption='AES256',
                    Metadata={'x-amz-crypto-instr-file': args.s3_key})
            else:
                s3.put_object(Bucket=args.bucket,
                    Key=args.s3_key+'.instruction',
                    Body=json.dumps(metadata),
                    ServerSideEncryption='AES256')


if __name__ == '__main__':
    main()