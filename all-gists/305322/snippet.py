"""
A helper for the app engine blobstore API and Django.

Works with the appengine patch:
http://code.google.com/p/app-engine-patch/

Taken and inspired by: 
http://appengine-cookbook.appspot.com/recipe/blobstore-get_uploads-helper-function-for-django-request/

Usage:

def upload_file(request):
    try:
        for upload in blogstore_helper.get_uploads(request,'file'):
            file = BlobFile(blob=upload)
            file.save()
        return HttpResponseRedirect("/redirect/to/file/viewer/")
    except:
        # throw an error
        return HttpResponseRedirect("/redirect/to/error/handler")

def serve_file(request, blob_id):
    blob_id = str(urllib.unquote(blob_id))
    blob = blobstore.BlobInfo.get(blob_id)
    return blogstore_helper.send_blob(request, blob, save_as=True)


awesome, 
harper@nata2.org
"""

import cgi 
from google.appengine.ext import blobstore
from django.http import HttpResponse
import logging

def get_uploads(request, field_name=None, populate_post=False):
    """Get uploads sent to this handler.

    Args:
      field_name: Only select uploads that were sent as a specific field.
      populate_post: Add the non blob fields to request.POST

    Returns:
      A list of BlobInfo records corresponding to each upload.
      Empty list if there are no blob-info records for field_name.
    """
    
    if hasattr(request,'__uploads') == False:
        request.META['wsgi.input'].seek(0) 
        fields = cgi.FieldStorage(request.META['wsgi.input'], environ=request.META)
        
        request.__uploads = {}
        if populate_post:
            request.POST = {}
        
        for key in fields.keys():
            field = fields[key]
            if isinstance(field, cgi.FieldStorage) and 'blob-key' in field.type_options:
                request.__uploads.setdefault(key, []).append(blobstore.parse_blob_info(field))
            elif populate_post:
                request.POST[key] = field.value

    if field_name:
        try:
            return list(request.__uploads[field_name])
        except KeyError:
            return []
    else:
        results = []
        for uploads in request.__uploads.itervalues():
            results += uploads
        return results


def send_blob(request, blob_key_or_info, content_type=None, save_as=None):
    """Send a blob-response based on a blob_key.

    Sets the correct response header for serving a blob.  If BlobInfo
    is provided and no content_type specified, will set request content type
    to BlobInfo's content type.

    Args:
      blob_key_or_info: BlobKey or BlobInfo record to serve.
      content_type: Content-type to override when known.
      save_as: If True, and BlobInfo record is provided, use BlobInfos
        filename to save-as.  If string is provided, use string as filename.
        If None or False, do not send as attachment.

      Raises:
        ValueError on invalid save_as parameter.
    """

    CONTENT_DISPOSITION_FORMAT = 'attachment; filename="%s"'
    if isinstance(blob_key_or_info, blobstore.BlobInfo):
      blob_key = blob_key_or_info.key()
      blob_info = blob_key_or_info
    else:
      blob_key = blob_key_or_info
      blob_info = None

    logging.debug(blob_info)
    response = HttpResponse()
    response[blobstore.BLOB_KEY_HEADER] = str(blob_key)

    if content_type:
      if isinstance(content_type, unicode):
        content_type = content_type.encode('utf-8')
      response['Content-Type'] = content_type
    else:
      del response['Content-Type']

    def send_attachment(filename):
      if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
      response['Content-Disposition'] = (CONTENT_DISPOSITION_FORMAT % filename)

    if save_as:
      if isinstance(save_as, basestring):
        send_attachment(save_as)
      elif blob_info and save_as is True:
        send_attachment(blob_info.filename)
      else:
        if not blob_info:
          raise ValueError('Expected BlobInfo value for blob_key_or_info.')
        else:
          raise ValueError('Unexpected value for save_as')

    return response


