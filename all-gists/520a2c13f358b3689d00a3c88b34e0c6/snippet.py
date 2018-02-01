from django.utils.safestring import mark_safe

def parser(text):
    ''' Convert plain text to HTML '''
    limits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    digits = '0123456789'
    # unicode xml safe
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # replace &nbsp; (160) with space (32)
    text = text.replace(chr(160), chr(32))
    # convert linebreaks
    text = ''.join(['<p> %s </p>' % l for l in text.splitlines() if l.strip()])
    # split text in words and parse each
    words = text.split()
    for index in range(len(words)):
        word = words[index]
        # unwrap word
        endswith = ''
        startswith = ''
        if word.endswith(('.', ',', '!', '?', ':', ';')):
            endswith = word[-1:]
            word = word[:-1]
        if word.endswith(')'):
            endswith = ')' + endswith
            word = word[:-1]
        if word.startswith('('):
            startswith = '('
            word = word[1:]
        # replace word
        if word.startswith(('http://', 'https://')):
            protocol, separator, address = word.partition('://')
            if address.startswith('www.'):
                address = address[4:]
            if address.endswith('/'):
                address = address[:-1]
            if len(address) > 24:
                address = address[:21] + '...'
            if address:
                word = '<a href="{0}" rel="external">{1}</a>'.format(word, address)
        elif word.startswith('@'):
            handle = word[1:]
            if handle and all(c in limits for c in handle):
                word = '<a href="/{0}/" rel="author">@{0}</a>'.format(handle)
        elif word.startswith('#'):
            handle = word[1:]
            if handle and all(c in digits for c in handle):
                word = '<a href="/re/{0}/" rel="alternate">#{0}</a>'.format(handle)
            elif handle and all(c in limits for c in handle):
                word = '<a href="/search/&#63;q=%23{0}" rel="tag">#{0}</a>'.format(handle)
        # wrap word
        words[index] = startswith + word + endswith
    text = ' '.join(words)
    return mark_safe(text)
