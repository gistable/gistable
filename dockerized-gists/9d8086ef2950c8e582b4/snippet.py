import sys
from urllib import urlencode
import requests
from urlparse import urlparse, parse_qs
from random import choice
import re


self_id = '10204360172032372' # your facebook id here
utc_bday = '2014-07-27 18:30:00' # utc timestamp of your birthday
unichar_pattern = re.compile(r'\\u.{4}')

thanks = ['Thanks! :-)', 'Thanks a lot :-)', 'Thank you! :-)']

wish_terms = reduce(lambda x, y: x + y,
                    map(lambda (x, y): ['%s %s' % (x, s) for s in y],
                        [('happy', ['birthday', 'bday', 'b\'day', 'returns']),
                         ('many', ['happy']),
                         ('wish', ['you', 'u'])]))


def build_start_url(fb_id, access_token):
    base_url = 'https://graph.facebook.com/%s/feed' % (fb_id,)
    params = {'since': utc_bday,
              'access_token': access_token}
    url = '%s?%s' % (base_url, urlencode(params))
    return url


def post_dict(post):
    if 'comments' not in post.keys():
        post['comments'] = {}
        post['comments']['data'] = []

    return {'id': post['id'],
            'from': post['from']['name'],
            'message': post.get('message', ''), # cheap hack alert!
            'type': post['type'],
            'comments': len(post['comments']['data'])}


def prepare_msg(message):
    message = message.lower().replace('!', '')
    message = re.sub(unichar_pattern, '', message)
    return message


def is_bday_wish(message):
    message = prepare_msg(message)
    return any(map(lambda x: message.find(x) > -1, wish_terms))


def get_wishes(url, acc=None):
    acc = [] if acc is None else acc
    params = parse_qs(urlparse(url).query)
    until = params.get('until')
    stop = False if until is None else int(until[0]) < utc_bday
    if stop:
        return acc
    else:
        print url
        req = requests.get(url)
        if req.status_code == 200:
            content = req.json()
            feed = map(post_dict, content['data'])
            wishes = filter(lambda x: all([x['type'] == 'status', # type is status
                                           x['from'] != self_id,
                                           x['comments'] == 0,
                                           is_bday_wish(x['message'])]),  # not already thanked
                            feed)
            next_url = content['paging']['next']
            return get_wishes(next_url, acc + wishes)


def send_thanks(wish, access_token):
    message = choice(thanks)
    payload = {'message': message}
    url = 'https://graph.facebook.com/%s/comments?access_token=%s' % (wish['id'], access_token)
    print 'Replying %s to %s' % (message, wish['from'])
    requests.post(url, data=payload)


if __name__ == '__main__':
    script, access_token = sys.argv
    url = build_start_url(self_id, access_token)
    wishes = get_wishes(url)
    for wish in wishes:
        # print wish
        send_thanks(wish, access_token)