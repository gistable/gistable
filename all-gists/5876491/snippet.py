import hashlib, hmac, mimetypes, os, time

from base64 import b64encode, b64decode
from calendar import timegm
from datetime import datetime
from email.utils import formatdate
from urllib import quote

from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError


AWS_S3_BUCKET_URL = "http://%(bucket)s.s3.amazonaws.com/%(path)s"
AWS_S3_CONNECT_TIMEOUT = 10
AWS_S3_REQUEST_TIMEOUT = 30


class S3Client(object):
  """
	AWS client that handles asynchronous uploads to S3 buckets
	"""
	def __init__(self, access_key=None, secret_key=None, bucket=None):
		super(S3Client, self).__init__()
		
		self.access_key = access_key
		self.secret_key = secret_key
		self.bucket = bucket

	def generate_url(self, path):
		"""
		Generates a URL for the given file path
		"""
		return AWS_S3_BUCKET_URL % {
			"bucket": self.bucket,
			"path": path,
		}

	def _guess_mimetype(self, filename, default="application/octet-stream"):
		"""
		Guess mimetype from file name
		"""
		if "." not in filename:
			return default

		prefix, extension = filename.lower().rsplit(".", 1)

		if extension == "jpg":
			extension = "jpeg"

		return mimetypes.guess_type(prefix + "." + extension)[0] or default

	def _aws_md5(self, data):
		"""
		Make an AWS-style MD5 hash (digest in base64)
		"""
		hasher = hashlib.new("md5")

		if hasattr(data, "read"):
			data.seek(0)

			while True:
				chunk = data.read(8192)

				if not chunk:
					break

				hasher.update(chunk)

			data.seek(0)
		else:
			hasher.update(data)

		return b64encode(hasher.digest()).decode("ascii")

	def _urlquote(self, url):
		"""
		Quote URLs in AWS format
		"""
		if isinstance(url, unicode):
			url = url.encode("utf-8")

		return quote(url, "/")

	def _rfc822_datetime(self, t=None):
		"""
		Generate date in RFC822 format
		"""
		if t is None:
			t = datetime.utcnow()

		return formatdate(timegm(t.timetuple()), usegmt=True)

	def _generate_authenticated_headers(self, method, path, headers={}):
		"""
		Generate headers for AWS with authentication tokens
		"""
		date = self._rfc822_datetime()

		signature = "\n".join([
			"{method}",
			"{content_md5}",
			"{content_type}",
			"{date}",
			"x-amz-acl:{acl}",
			"/{bucket}/{path}"
		]).format(
			method=method,
			acl=headers.get("X-Amz-Acl"),
			content_type=headers.get("Content-Type"),
			content_md5=headers.get("Content-MD5"),
			date=date,
			bucket=self._urlquote(self.bucket),
			path=self._urlquote(path)
		)

		auth_signature = b64encode(hmac.new(
			self.secret_key.encode("utf-8"),
			signature.encode("utf-8"),
			hashlib.sha1
		).digest()).strip()

		headers.update({
			"Date": date,
			"Authorization": "AWS %(access_key)s:%(auth_signature)s" % {
				"access_key": self.access_key,
				"auth_signature": auth_signature,
			}
		})

		return headers

	@coroutine	
	def upload(self, path, data, headers={}):
		"""
		Asynchronously uploads the given data stream to the specified path
		"""
		client = AsyncHTTPClient()
		method = "PUT"
		data = b64decode(data)

		headers.update({
			"Content-Length": str(len(data)),
			"Content-MD5": self._aws_md5(data),
			"X-Amz-Acl": "public-read",
			"Content-Type": self._guess_mimetype(path),
		})

		try:
			response = yield client.fetch(
				AWS_S3_BUCKET_URL % {
					"bucket": self.bucket,
					"path": path,
				},
				method=method,
				body=data,
				connect_timeout=AWS_S3_CONNECT_TIMEOUT,
				request_timeout=AWS_S3_REQUEST_TIMEOUT,
				headers=self._generate_authenticated_headers(
					method,
					path,
					headers=headers
				)
			)
		except HTTPError, error:
			raise Return(None)

		raise Return(response)
