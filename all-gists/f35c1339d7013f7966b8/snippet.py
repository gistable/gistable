#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2014, stf - AGPLv3+
# analyzes emails for netiquette
#
# invoke with mlint <emailcontainer> [<format>]
#
# where format is "mail" for raw mails, "mbox" for mbox files, if
# omitted the default is Maildir containers
#
# lints:
# - toppost: response is above quoted text
# - quotedsig: does not trim signatures from quotes
# - empty: empty email
# - quoteonly: contains only a quoted mail, no effective response
# - oneliner: contains only one effective response line
# - bigmedia: has multimedia attachment greater than 50KB
# - htmlonly: message does not contain a text/plain part
# - fancy: if no text/plain or encrypted content
# - longlines: uses lines longer than 80 chars (false positive can be caused also by urls)
# - bigdata: size of all attachments exceeds 200KB
# - quotebloat: quoted lines take more than (QUSNR*100)% of the effective response
# - nlbloat: excessive use of empty lines - more than (NLSNR*100)% of the effective response
# - longsig: signature is excessively long - false positive can be caused on mailing-list which append meta-info
# - fullquote: probably uses Outlook-style unquoted fullquote
# - nosubject: no subject given
# - SHOUTS: uses more than 50% caps in effective response

import mailbox, email, mimetypes, sys, os, re
from operator import itemgetter

MAXSIGLEN=4 # set to large val, if you don't want, or mailing-lists interfere.
NLSNR=0.6 # ratio of newlines to response
QUSNR=0.8 # ration of quote to response
MAXATT=1024*50 # max attachment size
MAXATTS=1024*200 # max total attachments size
MAXCOLS=80 # maximum width of text
SHOUTRATIO=0.5 # more than half of the letters are caps

cryptoheads = ['-----BEGIN PGP PUBLIC KEY BLOCK-----',
               '-----BEGIN PGP MESSAGE-----',]
cryptotails = ['-----END PGP PUBLIC KEY BLOCK-----',
               '-----END PGP MESSAGE-----',]

def delcrypto(lines):
    # cut out crypted content
    while True:
        inblock = False
        start=None
        for i, line in enumerate(lines):
            if not inblock:
                if lines[i].strip() in cryptoheads:
                    start = i
                    inblock=True
                    i+=2
            else:
                if lines[i].strip() in cryptotails:
                    break
        if start!=None:
            del lines[start:i+1]
        else:
            break
    return lines

def rate_msg(msg):
    # rates the content of the 1st text/plain message content
    res={}
    struct = []
    capsmap = []
    lines = msg.split('\n')
    if len(lines)==0:
        return {'empty':True}
    lines = delcrypto(lines)
    if len(lines)==0 or set(lines)==set(['']):
        return {}
    for i, line in enumerate(lines):
        if line == '-- ':
            try:
                sigsize = lines[i+1:].index('-- ')
            except ValueError:
                sigsize = len(lines) - (i+2)
            if sigsize > MAXSIGLEN:
                res['longsig']=sigsize
            break
        type = line.strip()[:1]
        if type not in ['','>']: type = 't'
        if (type == 't' and
            sum((1 for x in lines[i+1:] if x[:1] == '>')) == 0 and (
            line == '-----Original Message-----' or
            line == '________________________________' or
            (line.startswith("From: ") and lines[i-1].strip() == ''))):
                struct.append(['>', len(lines)-i])
                res['fullquote']=True
                break
        if len(struct)>0 and type == struct[-1][0]:
            struct[-1][1]+=1
        else:
            struct.append([type, 1])
        if type == 't' and len(line)>MAXCOLS:
            if not 'longlines' in res:
                res['longlines']=[len(line)]
            else:
                res['longlines'].append(len(line))
        if type == '>' and line.endswith('-- '):
            if not 'quotedsig' in res:
                res['quotedsig']=0
            res['quotedsig']+=1
        if type=='t':
            capsmap.extend([('a' if x.islower() else 'A') if x.isalpha() else ' ' for x in line])

    quotedlines = float(sum(x for t,x in struct if t == '>'))
    emptylines = float(sum(x for t,x in struct if t == ''))
    if len(lines)-emptylines==0:
        res['empty']=True
    elif quotedlines/(len(lines)-emptylines)>QUSNR:
        res['quotebloat']=quotedlines/(len(lines)-emptylines)
    if len(lines)-quotedlines==0:
        res['quoteonly']=True
    elif emptylines/(len(lines)-quotedlines)>NLSNR:
        res['nlbloat']=emptylines/(len(lines)-quotedlines)
    if len(lines)-emptylines-quotedlines==1:
        res['oneliner']=True
    #print struct
    tofulst = []
    for t,c in struct:
        if t=='': continue
        if len(tofulst)>0 and t == tofulst[-1][0]:
            tofulst[-1][1]+=c
        else:
            tofulst.append([t, c])
    if len(tofulst)==2 and tofulst[0][0]=='t' and tofulst[1][0]=='>':
        res['toppost']=float(tofulst[1][1])/tofulst[0][1]
    #print tofulst

    # check shouting
    capsmap = ''.join(capsmap)
    if capsmap:
        caps = capsmap.count('A')
        low = capsmap.count('a')
        if float(caps)/(low+caps)>SHOUTRATIO:
            res['SHOUTS']=True

    return res

def score(msg):
    res={}
    parts = msg.walk()
    types = []
    attsize = 0
    for part in parts:
        types.append(part.get_content_type())
        if part.get_content_type() == 'multipart/alternative' and not 'alts' in res:
            res['alts']=[]
            for apart in list(part.walk())[1:]:
                if apart.get_content_type() == 'text/plain' and 'text/plain' not in res['alts']:
                    res.update(rate_msg(apart.get_payload(decode=True)))
                if apart.get_content_maintype() == 'multipart': break
                res['alts'].append(apart.get_content_type())
            [parts.next() for _ in range(len(res['alts']))]
            continue
        if part.get_content_type() == 'multipart/encrypted':
            if not 'bodytype' in res:
                res['bodytype']='multipart/encrypted'
            cipher=[]
            for apart in list(part.walk())[1:]:
                if apart.get_content_maintype() == 'multipart': break
                cipher.append(apart.get_content_type())
            [parts.next() for _ in range(len(cipher))]
            continue
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get_content_maintype() in ['audio', 'image', 'video', 'application']:
            size = len(part.get_payload(decode=True))
            if size>MAXATT:
                if not 'bigmedia' in res:
                    res['bigmedia']=[(size, part.get_content_subtype())]
                else:
                    res['bigmedia'].append((size, part.get_content_subtype()))
                attsize+=size
            continue
        if not 'alts' in res and not 'bodytype' in res and part.get_content_maintype() == 'text':
            if part.get_content_type() == 'text/plain':
                res.update(rate_msg(part.get_payload(decode=True)))
            res['bodytype'] = part.get_content_type()

    tmp = res.get('alts',[])+[res.get('bodytype')]
    if 'alts' in res: del res['alts']
    if 'bodytype' in res: del res['bodytype']
    if [x for x in tmp if x] == ['text/html']:
        res['htmlonly']=True
    elif 'text/plain' not in tmp and tmp != ['multipart/encrypted']:
        res['fancy']=(tmp, types)
    if not 'bigmedia' in res and attsize>MAXATTS:
        res['bigdata']=size
    if not msg['subject'] or msg['subject'].strip() == '':
        res['nosubject']=True

    return res

def updatestats(lints, msg, stats):
    mail = email.utils.parseaddr(msg['from'])[1]
    if not mail in stats:
        stats[mail]={'name': mail, 'score': 0, 'msgcnt': 0}
    stats[mail]['msgcnt']+=1
    for k,v in lints.items():
        if not k in stats[mail]:
            stats[mail][k]=[v]
        else:
            stats[mail][k].append(v)
        stats[mail]['score']+=1

def printstats(stats):
    for sender in sorted(stats.values(),key=itemgetter('score'), reverse=True):
        if sender['score']==0: continue
        print "%-4s %s" % (sender['score'], sender['name'])
        print '\t%s' % '\n\t'.join("%-20s %s %d%%" % (k1,v1,float(v1)*100/sender['msgcnt'])
                                   for k1,v1
                                   in sorted(((k,len(v))
                                              for k, v in sender.items()
                                              if k not in ['name','score', 'msgcnt']),
                                             key=itemgetter(1), reverse=True))

stats={}

if 'mail' in sys.argv:
    # check one mail
    with open(sys.argv[1]) as fp:
        msg = email.message_from_file(fp)
    tmp = score(msg)
    if tmp:
        print msg['from'], msg['message-id']
        print '\t%s' % '\n\t'.join("%-20s %s" % (k,v) for k, v in tmp.items())
else:
    # check bag of mails
    if 'mbox' in sys.argv:
        del sys.argv[sys.argv.index('mbox')]
        container = mailbox.mbox(sys.argv[1])
    elif len(sys.argv)==2:
        container = mailbox.Maildir(sys.argv[1],factory=None)

    for k in container.iterkeys():
        try:
            msg = container[k]
        except email.errors.MessageParseError:
            print "[meh] malformed message", k
            continue

        tmp = score(msg)

        updatestats(tmp,msg,stats)
    printstats(stats)
