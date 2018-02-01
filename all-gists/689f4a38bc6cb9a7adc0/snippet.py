import random
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    headers = kwargs.get("headers", {})
    headers["X-Forwarded-For"] = "127.0.0.%s" % random.randint(1,254)
    return payload
