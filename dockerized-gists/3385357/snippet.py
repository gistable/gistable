# -*- coding: utf-8 -*-
import locale
import re

from flask import Flask, redirect, request
app = Flask(__name__)

LANGUAGE_CODES = ('fr', 'en', 'zh')
DOMAIN_NAME = 'example.com'

# From django.utils.translation.trans_real.to_locale
def to_locale(language, to_lower=False):
    """
    Turns a language name (en-us) into a locale name (en_US). If 'to_lower' is
    True, the last component is lower-cased (en_us).
    """
    p = language.find('-')
    if p >= 0:
        if to_lower:
            return language[:p].lower()+'_'+language[p+1:].lower()
        else:
            # Get correct locale for sr-latn
            if len(language[p+1:]) > 2:
                return language[:p].lower()+'_'+language[p+1].upper()+language[p+2:].lower()
            return language[:p].lower()+'_'+language[p+1:].upper()
    else:
        return language.lower()

# From django.utils.translation.trans_real.parse_accept_lang_header
accept_language_re = re.compile(r'''
        ([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*|\*)         # "en", "en-au", "x-y-z", "*"
        (?:\s*;\s*q=(0(?:\.\d{,3})?|1(?:.0{,3})?))?   # Optional "q=1.00", "q=0.8"
        (?:\s*,\s*|$)                                 # Multiple accepts per header.
        ''', re.VERBOSE)

def parse_accept_lang_header(lang_string):
    """
    Parses the lang_string, which is the body of an HTTP Accept-Language
    header, and returns a list of (lang, q-value), ordered by 'q' values.

    Any format errors in lang_string results in an empty list being returned.
    """
    result = []
    pieces = accept_language_re.split(lang_string)
    if pieces[-1]:
        return []
    for i in range(0, len(pieces) - 1, 3):
        first, lang, priority = pieces[i : i + 3]
        if first:
            return []
        priority = priority and float(priority) or 1.0
        result.append((lang, priority))
    result.sort(key=lambda k: k[1], reverse=True)
    return result

def normalize_language(language):
    return locale.locale_alias.get(to_locale(language, True))

def is_language_supported(language, supported_languages=None):
    if supported_languages is None:
        supported_languages = LANGUAGE_CODES
    if not language:
        return None
    normalized = normalize_language(language)
    if not normalized:
        return None
    # Remove the default encoding from locale_alias.
    normalized = normalized.split('.')[0]
    for lang in (normalized, normalized.split('_')[0]):
        if lang.lower() in supported_languages:
            return lang
    return None

def parse_http_accept_language(accept):
    for accept_lang, unused in parse_accept_lang_header(accept):
        if accept_lang == '*':
            break

        # We have a very restricted form for our language files (no encoding
        # specifier, since they all must be UTF-8 and only one possible
        # language each time. So we avoid the overhead of gettext.find() and
        # work out the MO file manually.

        # 'normalized' is the root name of the locale in POSIX format (which is
        # the format used for the directories holding the MO files).
        normalized = locale.locale_alias.get(to_locale(accept_lang, True))
        if not normalized:
            continue
        # Remove the default encoding from locale_alias.
        normalized = normalized.split('.')[0]

        for lang_code in (accept_lang, accept_lang.split('-')[0]):
            lang_code = lang_code.lower()
            if lang_code in LANGUAGE_CODES:
                return lang_code
    return None
    

@app.route('/')
def language_detection():
    """Select the right language

        1. CookieLanguageMiddleware : Look at the cookie if exists
        2. HttpAcceptLanguageMiddleware : Look at the browser language settings
        3. DefaultLanguageMiddleware : Come back to english

    """
    lang = None

    # Cookie
    if lang is None:
        lang_code = request.cookies.get('django_language', None)
        lang = is_language_supported(lang_code)
    
    # HttpAcceptLanguageMiddleware
    if lang is None:
        lang = parse_http_accept_language(request.headers.get('Accept-Language', ''))

    # DefaultLanguageMiddleware
    if lang is None:
        lang = 'en'

    return redirect('http://%s.%s/' % (lang, DOMAIN_NAME))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
