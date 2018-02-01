#! /usr/bin/env python

"""
Pounce on an open OpenTable reservation.
"""

import sys, os, time, re, mechanize, gtk, webkit, threading, random

rid = 1180 # OpenTable restaurant ID; 1180 = French Laundry
people_choices = [3, 3, 3, 4] # number of people to request for; cycles through choices
targetdate = parsedate ((5, 13, 2012, 7, 30, 00, 'PM'))
slop = 86400 # in seconds; = 1 day; default date tolerance
mintime = targetdate - slop # override manually if you want
maxtime = targetdate + slop

noisemaker_command = 'paplay /usr/share/sounds/gnome/default/alerts/bark.ogg'
noisemaker_interval = 3 # in seconds

timeout = 5 # in seconds; timeout for web request

# I don't know what (if any) robot prevention systems OpenTable uses ...
minperiod = 3 # shortest interval between requests
maxperiod = 9 # longest interval between requests

assert mintime < targetdate
assert maxtime > targetdate


def makequery (rid, date, people):
    query_url = 'http://opentable.com/opentables.aspx?t=rest&r=%d&d=%s&p=%d'
    return query_url % (rid, fmtdate (date), people)


def fmtdate (t):
    q = time.localtime (t)
    yr, mo, dy = q[:3]
    hr, mn, sc = q[3:6]
    if hr == 0:
        hr = 12
        sfx = 'AM'
    elif hr < 12:
        sfx = 'AM'
    else:
        hr -= 12
        sfx = 'PM'
    return '%d/%d/%d%%20%d:%02d:%02d%%20%s' % (mo, dy, yr, hr, mn, sc, sfx)


def parsedate (t):
    mo, dy, yr, hr, mn, sc = [int (x) for x in t[:6]]

    if t[6] == 'AM':
        if hr == 12:
            hr = 0
    elif t[6] == 'PM':
        if hr != 12:
            hr += 12

    return time.mktime ((yr, mo, dy, hr, mn, sc, 0, 0, -1))


def findhits (n, f, targetdate):
    datepattern = re.compile (r'\[\'(\d{1,2})\/(\d{1,2})\/(\d{4}) '
                              r'(\d{1,2})\:(\d{2})\:(\d{2}) ([AP]M)')
    pounces = []

    for l in f:
        dmatches = re.findall (datepattern, l)
        if not len (dmatches):
            continue

        for dt in dmatches:
            date = parsedate (dt)

            if date < mintime or date > maxtime:
                print n, time.strftime ('%Y/%m/%d %H:%M:%S'), '**rejecting**', fmtdate (date)
                continue

            score = abs (date - targetdate)
            pmatch = '[\'%s/%s/%s %s:%s:%s %s\'' % dt
            pounces.append ((score, date, pmatch))

    pounces.sort (key=lambda t: t[0])
    return pounces


def noisemaker ():
    while True:
        os.system (noisemaker_command)
        time.sleep (noisemaker_interval)


def pounce (qurl, pmatch):
    thr = threading.Thread (target=noisemaker)
    thr.start ()

    v = webkit.WebView ()
    w = gtk.Window ()
    w.connect ('destroy', lambda q: w.destroy)
    w.set_size_request (1000, 600)
    w.connect ('delete-event', lambda w, e: gtk.main_quit ())
    s = gtk.ScrolledWindow ()
    s.add (v)
    w.add (s)
    w.show_all ()

    myscript = r'''
    var lis = document.getElementsByTagName("li");
    for (var i = 0; i < lis.length; i++) {
      var a = lis[i].getAttribute ("a");
      if (a != null) {
        if (a.indexOf ("%s") == 0) {
          Time_OnClick (lis[i], GridType.ResultsGrid);
          break;
        }
      }
    }
    ''' % pmatch

    def finished (*args):
        if v.get_load_status () != webkit.LOAD_FINISHED:
            return
        v.execute_script (myscript)

    v.connect ('notify::load-status', finished)
    v.open (qurl)
    gtk.main ()


def iteration (n, targetdate):
    br = mechanize.Browser ()
    people = people_choices[n % len (people_choices)]
    qurl = makequery (rid, targetdate, people)
    print n, time.strftime ('%Y/%m/%d %H:%M:%S'), 'R:', qurl

    try:
        br.open (qurl, timeout=timeout)
    except mechanize.URLError:
        print n, time.strftime ('%Y/%m/%d %H:%M:%S'), '--> timeout'
        return

    pounces = findhits (n, br.response (), targetdate)
    if not len (pounces):
        print n, time.strftime ('%Y/%m/%d %H:%M:%S'), '--> no results'
        return

    score, date, pmatch = pounces[0]
    print n, time.strftime ('%Y/%m/%d %H:%M:%S'), 'GOT ONE:', date, pmatch, score
    pounce (qurl, pmatch)


n = 0

while True:
    try:
        iteration (n, targetdate)
    except Exception as e:
        print >>sys.stderr, n, 'EXCEPTION:', e

    time.sleep (random.uniform (minperiod, maxperiod))
    n += 1