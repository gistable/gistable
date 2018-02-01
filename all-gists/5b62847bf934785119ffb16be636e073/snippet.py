# coding: utf-8
import appex
from html2text import html2text
import console
import re

def main():
	if not appex.is_running_extension():
		print 'This script is intended to be run from the sharing extension.'
		return
	text = appex.get_attachments()
	if not text:
		print 'No text input found.'
		return
	console.alert('Statistics', '%s' % (text), 'OK', hide_cancel_button=True)

if __name__ == '__main__':
	main()
	