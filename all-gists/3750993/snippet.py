from urllib import quote
from string import ascii_lowercase
from operator import itemgetter
import os
import random
import requests
from datetime import datetime
from lib.languages import LANGUAGES, get_language_by_name
from lib.utils import format_timedelta

try:
    import json
except ImportError:
    import simplejson as json

#Set the user agent to a common browser user agent string to get always utf-8 encoded response
headers = {'User-agent':'Mozilla/5.0'}
languages = sorted(LANGUAGES, key=itemgetter('name'))
#proxy_list = ['http://uberminiproxy.appspot.com/', 
            #'http://uberminiproxy-1.appspot.com/', 
            #'http://uberminiproxy-2.appspot.com/',
            #'http://uberminiproxy-3.appspot.com/',
            #'http://uberminiproxy-4.appspot.com/']
#Alternative URL
#www.google.com/complete/search?hjson=true&qu=a

def get_suggestion(query, lang, tld, ds=''):
    """Query Google suggest service"""
    suggestions = []
    if query:
        if isinstance(query, unicode): 
            query = query.encode('utf-8')
        query = quote(query)
        url = "http://clients1.google.%s/complete/search?hl=%s&q=%s&json=t&ds=%s&client=serp" %(tld, lang, query, ds)
        #the_url = random.choice(proxy_list)
        #response = requests.get(the_url, headers=headers, params={'url':url})
        response = requests.get(url, headers=headers)
        if response.ok:
            result = json.loads(response.content)
            suggestions = [i for i in result[1]]
        else:
            pass #FIXME handle and display errors
    return suggestions

def get_news_suggestion(query, lang, country):
    suggestions = []
    if query:
        if isinstance(query, unicode): 
            query = query.encode('utf-8')
        query = quote(query)
        url = "http://news.google.com/complete/search?hl=%s&gl=%s&ds=n&nolabels=t&hjson=t&client=news&q=%s" %(lang, country, query)
        #the_url = random.choice(proxy_list)
        #response = requests.get(the_url, headers=headers, params={'url':url})
        response = requests.get(url, headers=headers)
        if response.ok:
            result = json.loads(response.content)
            suggestions = [i[0] for i in result[1]]
    return suggestions

def single_suggest(query, lang, source):
    """Provide suggestions via AJAX"""
    result = []
    language = get_language_by_name(lang)
    if source == 'web':
        result = get_suggestion(query, language['code'], language['tld'])
    elif source == 'pr':
        result = get_suggestion(query, language['code'], language['tld'], ds='pr')
    elif source == 'news':
        result = get_news_suggestion(query, language['code'], language['country'])
    return result[1:]

def single_letter_recursive_suggest(query, language, source):
    """Get suggestion and expand the query """
    
    selected_language = get_language_by_name(language)
    expansion = []
    chars = ascii_lowercase
    
    try:
        if source == 'web':
            gweb = get_suggestion(query, selected_language['code'], selected_language['tld'])
        elif source == 'pr':
            gweb = get_suggestion(query, selected_language['code'], selected_language['tld'], ds='pr')
        elif source == 'news':
            gweb = get_news_suggestion(query, selected_language['code'], selected_language['country'])
        for letter in chars:
            exp_query = query + ' ' + letter 
            if source == 'web':
                suggestions = get_suggestion(exp_query, selected_language['code'], selected_language['tld'])
            elif source == 'pr':
                suggestions = get_suggestion(query, selected_language['code'], selected_language['tld'], ds='pr')
            elif source == 'news':
                suggestions = get_news_suggestion(exp_query, selected_language['code'], selected_language['country'])
            if suggestions:
                expansion.append((letter, suggestions))

    except (IOError, ValueError), e:
        gweb = ''
        expansion = ''
    data = {'result':gweb, 'expansion':expansion, 'date':datetime.now()}
    code = selected_language['code']
    expansion_words = data['result']
    for ex in data['expansion']:
        expansion_words.extend(ex[1])
    return expansion_words

#Will this write the file - again
if __name__ == "__main__":
    print single_letter_recursive_suggest("patio door handle", "English/USA", "web")