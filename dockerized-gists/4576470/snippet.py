import urllib
import urlparse

def iri_to_uri(iri, encoding='Latin-1'):
    "Takes a Unicode string that can contain an IRI and emits a URI."
    scheme, authority, path, query, frag = urlparse.urlsplit(iri)
    scheme = scheme.encode(encoding)
    if ":" in authority:
        host, port = authority.split(":", 1)
        authority = host.encode('idna') + ":%s" % port
    else:
        authority = authority.encode(encoding)
    path = urllib.quote(
      path.encode(encoding), 
      safe="/;%[]=:$&()+,!?*@'~"
    )
    query = urllib.quote(
      query.encode(encoding), 
      safe="/;%[]=:$&()+,!?*@'~"
    )
    frag = urllib.quote(
      frag.encode(encoding), 
      safe="/;%[]=:$&()+,!?*@'~"
    )
    return urlparse.urlunsplit((scheme, authority, path, query, frag))