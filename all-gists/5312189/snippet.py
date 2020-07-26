import os, hashlib, re, math
import ecdsa

from ecdsa.util import string_to_number, number_to_string

############ hashing functions most from pywallet #####################

# secp256k1, http://www.oid-info.com/get/1.3.132.0.10
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
_b = 0x0000000000000000000000000000000000000000000000000000000000000007L
_a = 0x0000000000000000000000000000000000000000000000000000000000000000L
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8L
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp( _p, _a, _b )
generator_secp256k1 = ecdsa.ellipticcurve.Point( curve_secp256k1, _Gx, _Gy, _r )
oid_secp256k1 = (1,3,132,0,10)
SECP256k1 = ecdsa.curves.Curve("SECP256k1", curve_secp256k1, generator_secp256k1, oid_secp256k1 ) 

addrtype = 0

def Hash(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def public_key_to_bc_address(public_key):
	h160 = hash_160(public_key)
	return hash_160_to_bc_address(h160)

def hash_160(public_key):
	try:
		md = hashlib.new('ripemd160')
		md.update(hashlib.sha256(public_key).digest())
		return md.digest()
	except:
		import ripemd
		md = ripemd.new(hashlib.sha256(public_key).digest())
		return md.digest()

def hash_160_to_bc_address(h160):
	vh160 = chr(addrtype) + h160
	h = Hash(vh160)
	addr = vh160 + h[0:4]
	return b58encode(addr)

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
	""" encode v, which is a string of bytes, to base58. """

	long_value = 0L
	for (i, c) in enumerate(v[::-1]):
		long_value += (256**i) * ord(c)

	result = ''
	while long_value >= __b58base:
		div, mod = divmod(long_value, __b58base)
		result = __b58chars[mod] + result
		long_value = div
	result = __b58chars[long_value] + result

	# Bitcoin does a little leading-zero-compression:
	# leading 0-bytes in the input become leading-1s
	nPad = 0
	for c in v:
		if c == '\0': nPad += 1
		else: break

	return (__b58chars[0]*nPad) + result

def b58decode(v, length):
	""" decode v into a string of len bytes
	"""
	long_value = 0L
	for (i, c) in enumerate(v[::-1]):
		long_value += __b58chars.find(c) * (__b58base**i)

	result = ''
	while long_value >= 256:
		div, mod = divmod(long_value, 256)
		result = chr(mod) + result
		long_value = div
	result = chr(long_value) + result

	nPad = 0
	for c in v:
		if c == __b58chars[0]: nPad += 1
		else: break

	result = chr(0)*nPad + result
	if length is not None and len(result) != length:
		return None

	return result

def get_bcaddress_version(strAddress):
	""" Returns None if strAddress is invalid.  Otherwise returns integer version of address. """
	addr = b58decode(strAddress,25)
	if addr is None: return None
	version = addr[0]
	checksum = addr[-4:]
	vh160 = addr[:-4] # Version plus hash160 is what is checksummed                                                                                                    
	h3 = Hash(vh160)
	if h3[0:4] == checksum:
		return ord(version)
	return None


############ open wallet manipulation functions #####################

wallets = {}

def get_wallet_or_create(mpk):
	if mpk in wallets.keys():
		return wallets[mpk]
	w = Wallet(mpk.decode('hex'))
	wallets[mpk] = w
	return w

def get_new_address(mpk, nth_adress):
	w = get_wallet_or_create(mpk)
	return w.create_new_address(nth_adress, False)

def validate_address_format(address):
	address = address.strip()
	if re.match(r"[a-zA-Z1-9]{27,35}$", address) is None:
		return False
	elif get_bcaddress_version(address) is None:
		return False
	else:
		return True


############ open wallet class #####################

class Wallet:
	def __init__(self, mpk):
		self.main_public_key = mpk
		self.addresses = []
		self.change_addresses = []

	def get_sequence(self, nth_adress, for_change):
		return string_to_number( Hash( "%d:%d:"%(nth_adress,for_change) + self.main_public_key ) )

	def create_new_address(self, nth_adress, for_change):
		"""   Publickey(type,nth_adress) = Main_public_key + H(nth_adress|S|type)*point  """
		curve = SECP256k1
		if nth_adress <= 0:
			nth_adress = len(self.change_addresses) if for_change else len(self.addresses)
		z = self.get_sequence(nth_adress,for_change)
		main_public_key = ecdsa.VerifyingKey.from_string( self.main_public_key, curve = SECP256k1 )
		pubkey_point = main_public_key.pubkey.point + z*curve.generator
		public_key2 = ecdsa.VerifyingKey.from_public_point( pubkey_point, curve = SECP256k1 )
		address = public_key_to_bc_address( '04'.decode('hex') + public_key2.to_string() )
		if for_change:
			self.change_addresses.append(address)
		else:
			self.addresses.append(address)
		return address