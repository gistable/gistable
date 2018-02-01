# This code is under the MIT license.
# Inspired by this StackOverflow question:
http://stackoverflow.com/questions/3295405/creating-django-objects-with-a-random-primary-key

import struct
from Crypto.Cipher import DES
from django.db import models


def base36encode(number):
    """Encode number to string of alphanumeric characters (0 to z). (Code taken from Wikipedia)."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]


def base36decode(numstr):
    """Convert a base-36 string (made of alphanumeric characters) to its numeric value."""
    return int(numstr,36)


class EncryptedPKModelManager(models.Manager):
    """This manager allows models to be identified based on their encrypted_pk value."""
    def get(self, *args, **kwargs):
        encrypted_pk = kwargs.pop('encrypted_pk', None)
        if encrypted_pk:
            # If found, decrypt encrypted_pk argument and set pk argument to the appropriate value
            kwargs['pk'] = struct.unpack('<Q', self.model.encryption_obj.decrypt(
                struct.pack('<Q', base36decode(encrypted_pk))
            ))[0]
        return super(EncryptedPKModelManager, self).get(*args, **kwargs)


class EncryptedPKModel(models.Model):
    """Adds encrypted_pk property to children which returns the encrypted value of the primary key."""
    encryption_obj = DES.new('8charkey') # This 8 character secret key should be changed!

    def __init__(self, *args, **kwargs):
        super(EncryptedPKModel, self).__init__(*args, **kwargs)
        setattr(
            self.__class__,
            "encrypted_%s" % (self._meta.pk.name,),
            property(self.__class__._encrypted_pk)
        )

    def _encrypted_pk(self):
        return base36encode(struct.unpack('<Q', self.encryption_obj.encrypt(
            str(struct.pack('<Q', self.pk))
        ))[0])

    encrypted_pk = property(_encrypted_pk)

    class Meta:
        abstract = True


class ExampleModelManager(EncryptedPKModelManager):
    pass


class ExampleModel(EncryptedPKModel):
    objects = ExampleModelManager()
    example_field = models.CharField(max_length=32)


# Example usage:
# example_instance = ExampleModel.objects.get(pk=1)
# url_pk = example_instance.encrypted_pk
# ExampleModel.objects.get(encrypted_pk=url_pk)
