import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.Random import get_random_bytes


class Cipher(object):
	# This can be 16 (AES-128), 24 (AES-192), or 32 (AES-256)
	key_length = 32
	
	def __init__(self, secret, salt):
		self.secret = secret
		self.salt = salt
		
		# Get a key of the right length.
		self.key = HMAC.new(secret, salt, SHA256).digest()[:self.key_length]
		
	@staticmethod
	def get_random_iv():
		return get_random_bytes(AES.block_size)

	def encrypt(self, plaintext):
		iv = self.get_random_iv()
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return iv + cipher.encrypt(plaintext)
	
	def decrypt(self, ciphertext):
		iv = ciphertext[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return cipher.decrypt(ciphertext)[AES.block_size:]


class URLSafeCipher(Cipher):
	
	def encrypt(self, plaintext):
		ciphertext = super(URLSafeCipher, self).encrypt(plaintext)
		return base64.urlsafe_b64encode(ciphertext)
	
	def decrypt(self, b64ciphertext):
		ciphertext = base64.urlsafe_b64decode(b64ciphertext)
		return super(URLSafeCipher, self).decrypt(ciphertext)
