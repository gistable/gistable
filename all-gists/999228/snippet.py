from Crypto.Cipher import AES
import binascii
import re

ssn_re = re.compile(r"^\d{3}[-\ ]?\d{2}[-\ ]?\d{4}$")
class EncryptedSSNField(models.CharField):
    
    description = _('Adds transparent encryption/decryption (AES256 using pyCrypto) for US Social Security Numbers in the database.')
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 64
        super(EncryptedSSNField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if value is u'' or '' or None:
            return unicode(value)
        else:
            encobj1 = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, settings.SECRET_KEY[34:50])
            encobj2 = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, settings.SECRET_KEY[34:50])
            dec1 = encobj1.decrypt(binascii.a2b_hex(value))
            dec2 = encobj2.decrypt(binascii.a2b_hex(dec1))
            return unicode(dec2.rstrip())
    
    def get_prep_value(self, value):
        encobj1 = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, settings.SECRET_KEY[34:50])
        encobj2 = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, settings.SECRET_KEY[34:50])
        match = re.match(ssn_re, value)
        block_bytes = 16
        while len(value) < block_bytes:
            value += ' ' 
        if match:
            enc1 = binascii.b2a_hex(encobj1.encrypt(value))
            enc2 = binascii.b2a_hex(encobj2.encrypt(enc1))
            return unicode(enc2)
        else:
            raise ValueError(_('Please enter a valid U.S. Social Security Number.'))
    
    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'isnull':
            return value
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)