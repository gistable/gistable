from __future__ import absolute_import
import json
import sys
import re
import requests
import urllib
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
from urllib2 import urlopen
from urllib2 import Request
from bs4 import BeautifulSoup as Soup

agent = {'User-Agent':
    "Mozilla/4.0 (\
    compatible;\
    MSIE 6.0;\
    Windows NT 5.1;\
    SV1;\
    .NET CLR 1.1.4322;\
    .NET CLR 2.0.50727;\
    .NET CLR 3.0.04506.30\
    )"}

class ColoredText:
    """Colored text class
    
    source: https://github.com/zoncoen/python-ginger
    """
    colors = ['black', 'red', 'green', 'orange', 'blue', 'magenta', 'cyan', 'white']
    color_dict = {}
    for i, c in enumerate(colors):
        color_dict[c] = (i + 30, i + 40)

    @classmethod
    def colorize(cls, text, color=None, bgcolor=None):
        """Colorize text
        @param cls Class
        @param text Text
        @param color Text color
        @param bgcolor Background color
        """
        c = None
        bg = None
        gap = 0
        if color is not None:
            try:
                c = cls.color_dict[color][0]
            except KeyError:
                print("Invalid text color:", color)
                return(text, gap)

        if bgcolor is not None:
            try:
                bg = cls.color_dict[bgcolor][1]
            except KeyError:
                print("Invalid background color:", bgcolor)
                return(text, gap)

        s_open, s_close = '', ''
        if c is not None:
            s_open = '\033[%dm' % c
            gap = len(s_open)
        if bg is not None:
            s_open += '\033[%dm' % bg
            gap = len(s_open)
        if not c is None or bg is None:
            s_close = '\033[0m'
            gap += len(s_close)
        return('%s%s%s' % (s_open, text, s_close), gap)
    
def get_ginger_url(text):
    """Get URL for checking grammar using Ginger.
    
    source: https://github.com/zoncoen/python-ginger
    
    @param text English text
    @return URL
    """
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"

    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.urlencode([
        ("lang", "US"),
        ("clientVersion", "2.0"),
        ("apiKey", API_KEY),
        ("text", text)])
    fragment = ""

    return(urlparse.urlunparse((scheme, netloc, path, params, query, fragment)))

def get_ginger_result(text):
    """Get a result of checking grammar.
    
    source: https://github.com/zoncoen/python-ginger
    
    @param text English text
    @return result of grammar check by Ginger
    """
    url = get_ginger_url(text)

    try:
        response = urllib.urlopen(url)
    except urllib2.HTTPError as e:
        print("HTTP Error:", e.code)
    except URLError as e:
        print("URL Error:", e.reason)
    except IOError, (errno, strerror):
        print("I/O error (%s): %s" % (errno, strerror))
    try:
        result = json.loads(response.read().decode('utf-8'))
    except ValueError:
        print("Value Error: Invalid server response.")

    return(result)

def correct_en(text):
    if len(text) > 600:
        print("You can't check more than 600 characters at a time.")
    fixed_text = text
    results = get_ginger_result(text)

    # Correct grammar
    if(not results["LightGingerTheTextResult"]):
        return(text + "  - Good English! :)")

    # Incorrect grammar
    color_gap, fixed_gap = 0, 0
    for result in results["LightGingerTheTextResult"]:
        if(result["Suggestions"]):
            from_index = result["From"] + color_gap
            to_index = result["To"] + 1 + color_gap
            suggest = result["Suggestions"][0]["Text"]

            # Colorize text
            colored_incorrect = ColoredText.colorize(text[from_index:to_index], 'red')[0]
            colored_suggest, gap = ColoredText.colorize(suggest, 'green')

            text = text[:from_index] + colored_incorrect + text[to_index:]
            fixed_text = fixed_text[:from_index-fixed_gap] + colored_suggest + fixed_text[to_index-fixed_gap:]

            color_gap += gap
            fixed_gap += to_index-from_index-len(suggest)
    return(fixed_text)

def translatekoen(text):
    """Returns the translation using google translate
    source: https://github.com/mouuff/mtranslate
    """
    base_link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s"
    if (sys.version_info[0] < 3):
        to_translate = urllib.quote_plus(text.encode('utf8'))
        link = base_link % ('en', 'ko', to_translate)
        request = Request(link, headers=agent)
        page = urlopen(request).read()
    else:
        to_translate = urllib.parse.quote(text.encode('utf8'))
        link = base_link % ('en', 'ko', to_translate)
        request = urllib.request.Request(link, headers=agent)
        page = urllib.request.urlopen(request).read().decode("utf-8")
    expr = r'class="t0">(.*?)<'
    result = re.findall(expr, page)
    if (len(result) == 0):
        return ("")
    return(result[0])

def koen(line, cell):
    translated_en = translatekoen(cell)
    corrected_en = correct_en(translated_en)
    print('Translated (Korean to English): ' + translated_en)
    print("")
    print("Grammar checked (English) : " + corrected_en)
    
def load_ipython_extension(shell):
    shell.register_magic_function(koen, 'cell')