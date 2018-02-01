#
# HashUtils - Simple functions derivated from standard Python hashlib.
#

__author__ = 'Mauro Baraldi (mauro@visie.com.br)'
__version__ = '0.0.2: February 17, 2011'

import re
import hashlib
from datetime import datetime

class Hash:
        """Common facilities using hashlib standard lib. Algotrithm used in all
        methods: MD5
        Returns of method is hashlib.md5(object_to_hash).hexdigest()

        Example of use:

        from hashutils import Hash
        h = Hash()
        >>> h.now_hash()
        'b3036f7831dc1394f1dcb6b989561d79'
        >>> h.today_hash()
        'b3036f7831dc1394f1dcb6b989561d79'
        >>> h.string_hash("My name is Earl.")
        'ad05d8348194adf6d6190a2ae550e099'
        >>> h.file_hash('/home/mauro/passwords.txt')
        '404627e52574140007692512e3ce2fa9'
        >>> h.file_hash('/home/mauro/passwords.txt', 1024)
        '997dd0044bc676fdf3f9db0560e642d0'
        >>> h.from_date_hash((2001, 3, 1, 12, 45), '%Y/%m/%d %H:%M')
        'fc573499016722e5ff0747f2dc7f4971'
        """
	def __init__(self):
		pass
		
	def today_hash(self):
		""" Return hash form datetime.today() function in format %Y%m%d """
		self.today = datetime.today().strftime('%Y%m%d')
		return hashlib.md5(self.today).hexdigest()

	def now_hash(self):
		""" Return hash form datetime.today() function in format %Y%m%d%H%M%S """
		self.today = datetime.today().strftime('%Y%m%d')
		return hashlib.md5(self.today).hexdigest()

	def from_date_hash(self, date, strfmt):
		""" Return hash form date in datetime.date format (%Y%m%d) """
		self.format = re.compile('[a-zA-z]').sub('d', strfmt)
		self.build_date = datetime.strptime(self.format % date, strfmt)
		self.date = self.build_date.strftime(strfmt)
		return hashlib.md5(self.date).hexdigest()

	def string_hash(self, string):
		""" Return hash form a given string. """
		return hashlib.md5(string).hexdigest()

	def file_hash(self, fp, size=128):
		""" Return hash form a given file. Default first 128 bytes."""
		with open(fp, 'r+') as temp:
			return hashlib.md5(temp.read(size)).digest()
