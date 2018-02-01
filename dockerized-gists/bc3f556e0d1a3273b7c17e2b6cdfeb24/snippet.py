"""
Experiments in removing contiguous slashes in URLs.
Why doesn't urlparse do this for us?
"""

import posixpath
import re
import urlparse

apiBaseURL = 'http://example.org//api/v1/'
apiQueryURI = '/search///////items/////?name=fubar'

# The problem: Too many contiguous slashes
apiFullURL = apiBaseURL + '/' + apiQueryURI
print apiFullURL  # http://example.org//api/v1///search//items?name=fubar

# Attempt 1: Fewer slashes, but still too many
apiFullURL = apiBaseURL.strip('/') + '/' + apiQueryURI.strip('/')
print apiFullURL  # http://example.org//api/v1/search//items?name=fubar

# Attempt 2: Maybe safer than above, but similar results
apiFullURL = apiBaseURL.rstrip('/') + '/' + apiQueryURI.lstrip('/')
print apiFullURL  # http://example.org//api/v1/search//items?name=fubar

# Attempt 3: A regex works, but is it safe? (Now we have two problems.)
apiFullURL = apiBaseURL + '/' + apiQueryURI
newApiFullURL = re.sub(r'([^:])/+', r'\1/', apiFullURL)
print newApiFullURL  # http://example.org/api/v1/search/items?name=fubar

# Attempt 4: The code below is longer, but works safely

# Parse the URL into parts as a mutable, ordered dictionary
apiFullURLParts = urlparse.urlparse(apiBaseURL + '/' + apiQueryURI)._asdict()

# POSIX path normalization is simple, but leaves 1-2 leading slashes
apiFullURLParts['path'] = posixpath.normpath(apiFullURLParts['path'].strip('/'))

# Success! No contiguous slashes
newApiFullURL = urlparse.urlunparse(apiFullURLParts.values())
print newApiFullURL  # http://example.org/api/v1/search/items?name=fubar
