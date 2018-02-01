import Crypto.Random
from Crypto.Protocol import KDF
from google.appengine.ext import ndb
from datetime import datetime

class Credentials(ndb.Model):
    """Credentials to authenticate a person.
    """
    # --- Class Variables ---
    # Our pseudo-random stream - used for generating random bits for the
    # salt and for iterations entropy
    _randf = None

    # --- Constants ---
    # Keep track of the basic number of iterations for our derived key,
    # which is stored with the key.
    ITERATIONS_2013 = 60000

    # Arbitrary, constant offset, not stored with the key but in the code.
    ITER_OFFSET = -257

    # Length of the stored key.
    DK_LEN = 32

    # --- Datastore variables ---
    # A derived key from e.g. PBKDF2 (or, future: scrypt)
    dk = ndb.BlobProperty(indexed=False)

    # The salt; randomly generated for each dk.
    salt = ndb.BlobProperty(indexed=False)

    # The number of KDF iterations, starting from ITERATIONS_2013 plus or
    # minus a small random amount, and increasing in amount over time to
    # compensate for increasing computational power.
    iterations = ndb.IntegerProperty(indexed=False)

    # --- OTHER ---
    # The next couple items are not part of this article, but included
    # as food for thought.

    # We keep track of how many times a person has attempted to log in.
    failed_attempts = ndb.IntegerProperty(indexed=False)

    # Computers authorized is a map from a uuid to an object with a date
    # and list of IP addresses.
    computers_authorized = ndb.JsonProperty()

    # Two factor authentication.
    other_factor = ndb.StringProperty(indexed=False)
    
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "<Credentials: {}>".format(dict(
            failed_attempts=self.failed_attempts
        ))
        
    @property
    def random_stream(self):
        if not self._randf:
            self._randf = Crypto.Random.new()
        return self._randf
        
    def _multiplier(self):
        """The multiplier to increase the KDF over time.

        The integer returned doubles every two years from 2013.
        """
        start = datetime(2013, 1, 1)
        now = datetime.now()
        return 2 ** ((now - start).days / 730.0)

    def _iterations(self):
        """The number of iterations for this KDF
        """
        # Increase exponentially, to grow with computation power
        base_iters = int(self.ITERATIONS_2013 * self._multiplier())

        # Entropy is an int < 65536, limited to 6% of the base iters.
        entropy = int(
            self.random_stream.read(2).encode('hex'), 16
        ) % int(base_iters * 0.06)

        # Return a sensible number of iterations;
        return base_iters + entropy

    def generate_dk(self, token):
        """Generate a defined key for a given token in hex
        >>> c = Credentials()
        >>> c.salt = 'abc'
        >>> c.iterations = 4
        >>> dk = c.generate_dk("password")
        >>> len(dk)
        64
        """
        return KDF.PBKDF2(token, self.salt, dkLen=self.DK_LEN,
                          count=self.iterations + self.ITER_OFFSET
                          ).encode('hex')
                          
    def set_dk(self, token):
        """Set the derived key from the given token, generating iterations
        and salt as necessary.

        >>> c = Credentials()
        >>> c.set_dk("password")
        >>> len(c.dk)
        64
        >>> len(c.salt)
        64
        >>> c.iterations >= c.ITERATIONS_2013
        True
        """
        self.iterations = self._iterations()
        self.salt = self.random_stream.read(32).encode('hex')
        self.dk = self.generate_dk(token)
        
    def verify(self, token):
        """Determine if the given token matches the saved token
        >>> c = Credentials()

        Fail when credentials have no dk
        >>> c.verify("password")

        # my name is my passport, verify me
        >>> c.set_dk("password")
        >>> c.verify("password")
        True

        # try a bad password
        >>> c.verify("not the password")
        False
        """
        if not self.dk:
            # If this user has no password, we cannot verify against it.
            # Our return value should still be falsy.
            return

        return self.dk == self.generate_dk(token)