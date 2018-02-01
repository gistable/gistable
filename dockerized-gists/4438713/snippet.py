def unicode_or_bust(raw_text):
    """Return the given raw text data decoded to unicode.

    If the text cannot be decoded, return None.

    """
    encodings = ["utf-8"]
    for encoding in (sys.getfilesystemencoding(), sys.getdefaultencoding()):
        # I would use a set for this, but they don't maintain order.
        if encoding not in encodings:
            encodings.append(encoding)

    for encoding in encodings:
        if encoding:  # getfilesystemencoding() may return None
            try:
                decoded = unicode(raw_text, encoding=encoding)
                return decoded
            except UnicodeDecodeError:
                pass

    # If none of those guesses worked, let chardet have a go.
    encoding = chardet.detect(raw_text)["encoding"]
    if encoding and encoding not in encodings:
        try:
            decoded = unicode(raw_text, encoding=encoding)
            return decoded
        except UnicodeDecodeError:
            pass
        except LookupError:
            pass

    # I've heard that decoding with cp1252 never fails, so try that last.
    try:
        decoded = unicode(raw_text, encoding="cp1252")
        return decoded
    except UnicodeDecodeError:
        pass

    # If nothing worked then give up.
    return None