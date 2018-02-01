# generates the aws canonical string for the given parameters
def canonical_string(method, path, headers, expires=None,
                     provider=None):
    if not provider:
        provider = boto.provider.get_default()
    interesting_headers = {}
    for key in headers:
        lk = key.lower()
        if headers[key] != None and (lk in ['content-md5', 'content-type', 'date'] or
                                     lk.startswith(provider.header_prefix)):
            interesting_headers[lk] = headers[key].strip()

    # these keys get empty strings if they don't exist
    if not interesting_headers.has_key('content-type'):
        interesting_headers['content-type'] = ''
    if not interesting_headers.has_key('content-md5'):
        interesting_headers['content-md5'] = ''

    # just in case someone used this.  it's not necessary in this lib.
    if interesting_headers.has_key(provider.date_header):
        interesting_headers['date'] = ''

    # if you're using expires for query string auth, then it trumps date
    # (and provider.date_header)
    if expires:
        interesting_headers['date'] = str(expires)

    sorted_header_keys = interesting_headers.keys()
    sorted_header_keys.sort()

    buf = "%s\n" % method
    for key in sorted_header_keys:
        val = interesting_headers[key]
        if key.startswith(provider.header_prefix):
            buf += "%s:%s\n" % (key, val)
        else:
            buf += "%s\n" % val

    # don't include anything after the first ? in the resource...
    buf += "%s" % path.split('?')[0]

    # ...unless there is an acl or torrent parameter
    if re.search("[&?]acl($|=|&)", path):
        buf += "?acl"
    elif re.search("[&?]policy($|=|&)", path):
        buf += "?policy"
    elif re.search("[&?]logging($|=|&)", path):
        buf += "?logging"
    elif re.search("[&?]torrent($|=|&)", path):
        buf += "?torrent"
    elif re.search("[&?]location($|=|&)", path):
        buf += "?location"
    elif re.search("[&?]requestPayment($|=|&)", path):
        buf += "?requestPayment"
    elif re.search("[&?]versions($|=|&)", path):
        buf += "?versions"
    elif re.search("[&?]versioning($|=|&)", path):
        buf += "?versioning"
    else:
        m = re.search("[&?]versionId=([^&]+)($|=|&)", path)
        if m:
            buf += '?versionId=' + m.group(1)

    return buf
