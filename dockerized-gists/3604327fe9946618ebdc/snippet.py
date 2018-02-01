#!/usr/bin/env python
# coding:utf-8
import StringIO
import os
import uuid

import restless.exceptions
import restless.serializers
import restless.tnd
import tornado.httputil


class SnippetUploaderSerializer(restless.serializers.Serializer):
    # Usage
    # class SnippetResource(restless.tnd.TornadoResource):
    #   serializer = helpers.SnippetUploaderSerializer()


    def deserialize(self, body):
        args = dict()
        post_data_multipart_files = dict()

        # We need the boundary string 8d1e7a823982469d82c0358769ccba4c from body
        """--8d1e7a823982469d82c0358769ccba4c
        Content-Disposition: form-data; name="file"; filename="test.txt"

        Test.txt content

        --8d1e7a823982469d82c0358769ccba4c--
        """

        boundary_string = StringIO.StringIO(body).readline()[2:].strip()
        tornado.httputil.parse_multipart_form_data(
            boundary=boundary_string, data=body,
            arguments=args, files=post_data_multipart_files)

        # Parse args
        for multipartfile in post_data_multipart_files.get('file') or []:
            if multipartfile:

                body, content_type, filename = multipartfile.values()
                unique_file_name = "%s" % uuid.uuid4()
                fullpath = os.path.abspath('uploads/%s' % unique_file_name)

                if content_type in ['application/unknown']:
                    content_type = 'text/plain'

                # Write `body` to a file, upload to S3 or GridFS etc.
                # You can use content_type comes from multi_part file also.

                # Upload file to file physical file system
                with open(fullpath, 'wb') as f:
                    f.write(body)
        # You can return uploaded urls, GridFS ObjectIDs, filenames, or any dictionary data that
        # would be used if Restless
        # I use MongoEngine ORM and returning GridFS metadatas for file uploads.

        # {
        #     'id': snippet.id.__str__(),
        #     'grid_id': snippet.file.grid_id.__str__(),
        #     'collection': snippet.file.collection_name,
        #     'file': {
        #         'id': snippet.file.gridout._id.__str__(),
        #         'content_type': snippet.file.gridout.content_type,
        #         'filename': snippet.file.gridout.filename,
        #         'length': snippet.file.gridout.length,
        #         'md5': snippet.file.gridout.md5,
        #         'metadata': snippet.file.gridout.metadata,
        #         'name': snippet.file.gridout.name,
        #         'upload_date': snippet.file.gridout.upload_date.__str__()
        #     }
        # }

        return []
