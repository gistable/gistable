def utf8(string):
    """Convert any string - bytes or unicode - to a str (i.e. unicode on
    Python 3, utf-8 encoded bytes on Python 2).
    """
    if config.python3:
        if isinstance(string, bytes):
            return string.decode('utf-8')    # Hope it was UTF-8 encoded!
    else:
        # Python 2:
        if isinstance(string, unicode):
            return string.encode('utf-8')
    
    # String is already a str
    return string