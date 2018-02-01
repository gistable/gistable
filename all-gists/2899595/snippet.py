"""
This file provides an eventlet based S3 uploader for django-ajax-uploader. It
supports chunk retry and chunk parallelism for efficient uploads.

This backend will only work with the forked django-ajax-uploader from my
multipart-post branch which adds some efficiencies to file upload.

django-ajax-uploader: https://github.com/brosner/django-ajax-uploader/tree/multipart-post

Author: Brian Rosner <brosner@gmail.com>
"""
import functools
import io

from django.conf import settings

import boto
import boto.s3.key
import eventlet

from ajaxuploader.backends.base import AbstractUploadBackend


class S3UploadBackend(AbstractUploadBackend):
    
    POOL_SIZE = 10
    CHUNK_RETRIES = 5
    
    def setup(self, filename):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.lookup(settings.AWS_BUCKET_NAME)
    
    def basic_upload(self, uploaded, filename):
        """
        Uploads the uploaded file to S3 using 
        """
        key = boto.s3.key.Key(self.bucket)
        key.key = filename
        key.set_contents_from_file(uploaded)
        return True
    
    def multipart_upload(self, uploaded, filename):
        """
        Uploads the uploaded file to S3 using multipart upload.
        """
        mp = self.bucket.initiate_multipart_upload(filename)
        def upload_chunk(chunk, c):
            with io.BytesIO(chunk) as buf:
                for x in xrange(self.CHUNK_RETRIES):
                    try:
                        mp.upload_part_from_file(buf, c)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        # rety the chunk again
                        buf.seek(0)
                        continue
                    else:
                        # chunk uploaded successfully; stop retrying
                        break
                else:
                    return False
            return True
        def produce_chunks():
            c = 1
            for chunk in uploaded.chunks(chunk_size=1024*1024*5):
                yield (chunk, c)
                c += 1
        pool = eventlet.GreenPool(self.POOL_SIZE)
        workers = pool.starmap(upload_chunk, produce_chunks())
        result = all(workers)
        mp.complete_upload()
        return result
    
    def upload(self, uploaded, filename):
        # if file is less than 5MB we fall-back to a basic upload (due to
        # chunk size restrictions.)
        if uploaded.size < (1024*1024*5):
            return self.basic_upload(uploaded, filename)
        else:
            return self.multipart_upload(uploaded, filename)
