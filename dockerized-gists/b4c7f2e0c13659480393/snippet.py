def is_url(url):
    parsed_url = urlparse.urlparse(url)
    return bool(parsed_url.scheme)