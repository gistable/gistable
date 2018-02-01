"""
Fix for some issues with the original code from Heroku:
	https://devcenter.heroku.com/articles/s3-upload-python
	
This example is also designed for use with Django, not Flask as in the original.
"""

import base64
import hashlib
import hmac
import logging
import os
import time
import urllib
from hashlib import sha1

from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render

from .forms import UploadForm


logger = logging.getLogger(__name__)

def upload(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = UploadForm(request.POST, request.FILES)
		# check whether it's valid:
		if form.is_valid():
			return HttpResponseRedirect('/uploads/done/')

	# if a GET (or any other method) we'll create a blank form
	else:
		form = UploadForm()

	return render(request, 'uploads/upload_form.html', {'form': form})

def sign_s3(request):
	"""
	https://devcenter.heroku.com/articles/s3-upload-python
	"""
	AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
	AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
	S3_BUCKET = os.environ.get('S3_BUCKET')

	object_name = urllib.parse.quote_plus(request.GET['file_name'])
	mime_type = request.GET['file_type']

	secondsPerDay = 24*60*60
	expires = int(time.time()+secondsPerDay)
	amz_headers = "x-amz-acl:public-read"

	string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

	encodedSecretKey = AWS_SECRET_KEY.encode()
	encodedString = string_to_sign.encode()
	h = hmac.new(encodedSecretKey, encodedString, sha1)
	hDigest = h.digest()
	signature = base64.encodebytes(hDigest).strip()
	signature = urllib.parse.quote_plus(signature)
	url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

	return JsonResponse({
		'signed_request': '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
		'url': url,
	})

def submit_form():
	username = request.form["username"]
	full_name = request.form["full_name"]
	avatar_url = request.form["avatar_url"]
	update_account(username, full_name, avatar_url)
	return redirect(url_for('profile'))