
from __future__ import unicode_literals
from youtube_dl import YoutubeDL
import boto3
import os

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		print(msg)

	def error(self, msg):
		print(msg)

client = boto3.client('s3')
bucket = 'your-bucket-name'

def upload(d):
	filename = "{0}-{1}.mp3".format(str(d['title']), str(d['id']))
	filepath = "/tmp/{0}".format(filename)
	client.upload_file(filepath, bucket, filename)
	client.put_object_acl(ACL='public-read', Bucket=bucket, Key=filename)
	region = "us-west-2"
	return "https://s3-%s.amazonaws.com/{0}/{1}".format(region, bucket, filename)

def processing_hook(d):
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')

def run(event, context):
	url = event['url']
	ydl_opts = {
		'outtmpl': '/tmp/%(title)s-%(id)s.%(ext)s',
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'logger': Logger(),
		'progress_hooks': [processing_hook],
		'ffmpeg_location': 'ffmpeg/',
	}

	ydl = YoutubeDL(ydl_opts)
	ydl.add_default_info_extractors()
	info = ydl.extract_info(url, True)

	response = upload(info)
	return { "url" : response }
