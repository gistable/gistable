import hashlib

def get_avatar_or_identicon(email, size=40):
    """Gets an avatar or identicon from Gravatar."""
    email_hash = hashlib.md5(email.lower()).hexdigest()
    return "http://www.gravatar.com/avatar/{0}?&r=PG&s={1}&default=identicon".format(email_hash, size)
