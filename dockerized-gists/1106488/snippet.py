def accept_languages(browser_pref_langs):
    """Parses the request and return language list.        
    browser_pref_langs is the plain Accept-Language http request header 
    value.
    Stolen from Products.PloneLanguageTool, under GPL (c) Plone Foundation,
    slightly modified.
    Taken from tweetengine http://github.com/Arachnid/tweetengine/
    """
    browser_pref_langs = browser_pref_langs.split(',')
    i = 0
    langs = []
    length = len(browser_pref_langs)
    # Parse quality strings and build a tuple like
    # ((float(quality), lang), (float(quality), lang))
    # which is sorted afterwards
    # If no quality string is given then the list order
    # is used as quality indicator
    for lang in browser_pref_langs:
        lang = lang.strip().lower().replace('_', '-')
        if lang:
            l = lang.split(';', 2)
            quality = []
            if len(l) == 2:
                try:
                    q = l[1]
                    if q.startswith('q='):
                        q = q.split('=', 2)[1]
                        quality = float(q)
                except:
                    pass
            if quality == []:
                quality = float(length-i)
            language = l[0]            
            langs.append((quality, language))
            if '-' in language:
                baselanguage = language.split('-')[0]
                langs.append((quality-0.001, baselanguage))
            i = i + 1
    # Sort and reverse it
    langs.sort()
    langs.reverse()
    # Filter quality string
    langs = map(lambda x: x[1], langs)
    return langs
