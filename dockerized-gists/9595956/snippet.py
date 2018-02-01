import hashlib
import sys
from uuid import UUID

text = sys.stdin.read()
print UUID(hashlib.sha256(text).hexdigest()[:32])
