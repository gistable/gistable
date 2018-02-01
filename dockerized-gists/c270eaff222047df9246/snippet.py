#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import smtplib
import time
import ConfigParser
import json
import os
from email.mime.text import MIMEText


last_log_id = None

content_tmpl = '''
<html>
<head><meta http-equiv=Content-Type content="text/html;charset=utf-8"><title>{title}</title></head>
<body>{body}</body>
</html>
'''

comment_tmpl = '''
<p><a href="mailto:{email}">{name}</a> 于 {time} 在文章《<a href="{url}">{title}</a>》下发表了评论：</p>
<p>{content}</p>
'''


def prepare_content(comments):
    global content_tmpl, comment_tmpl
    comments = [comment_tmpl.format(**comment) for comment in comments]
    content = content_tmpl.format(title='多说', body=''.join(comments))
    return content


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def get_response(base_url, params):
    url = '{}?{}'.format(base_url, urllib.urlencode(params))
    try:
        data = urllib.urlopen(url).read()
        resp = convert(json.loads(data))
        if resp['code'] != 0:
            return None
        return resp
    except Exception, e:
        print str(e)
        return None


def check(duoshuo):
    global last_log_id
    log_data = get_response('http://api.duoshuo.com/log/list.json', {
        'short_name': duoshuo['short_name'],
        'secret': duoshuo['secret'],
        'order': 'desc'
    })
    if log_data is None:
        return None

    comments = []
    if last_log_id:
        for log in log_data['response']:
            if log['log_id'] == last_log_id:
                break
            if log['action'] == 'create' and log['meta']['author_name'] != duoshuo['short_name']:
                thread_data = get_response('http://api.duoshuo.com/threads/listPosts.json', {
                    'short_name': duoshuo['short_name'],
                    'thread_key': log['meta']['thread_key']
                })
                comments.append({
                    'title': log['meta']['thread_key'],
                    'url': thread_data['thread']['url'] if thread_data else '',
                    'name': log['meta']['author_name'],
                    'email': log['meta']['author_email'],
                    'content': log['meta']['message'],
                    'time': log['meta']['created_at'].split('+')[0].replace('T', ' ')
                })
    last_log_id = log_data['response'][0]['log_id']
    return comments


def send_email(email, content):
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = '多说评论通知'
    msg['From'] = email['from']
    msg['To'] = email['to']
    msg['X-Mailer'] = 'Microsoft Outlook 14.0'
    try:
        server = smtplib.SMTP()
        server.connect(email['host'])
        server.login(email['name'], email['password'])
        server.sendmail(email['from'], [email['to']], msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


def read_conf():
    conf = ConfigParser.ConfigParser()
    path = os.path.dirname(__file__)
    conf_file = os.path.join(path, 'duoshuo.conf')
    conf.read(conf_file)

    duoshuo = dict(conf.items('duoshuo'))
    email = dict(conf.items('email'))
    return duoshuo, email


def run():
    global last_log_id
    duoshuo, email = read_conf()
    log_id_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'last_log_id')
    if os.path.exists(log_id_file):
        last_log_id = open(log_id_file).read()

    print '=> checking comments ...'
    comments = check(duoshuo)
    if comments:
        print '{} new comments found.'.format(len(comments))
        content = prepare_content(comments)
        print '=> sending email ...'
        send_email(email, content)
    open(log_id_file, 'w').write(last_log_id)


if __name__ == '__main__':
    run()
