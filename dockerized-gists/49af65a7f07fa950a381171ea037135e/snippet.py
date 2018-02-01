#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by zhuyifei1999 (https://wikitech.wikimedia.org/wiki/User:Zhuyifei1999)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import os
import re
import time
#import datetime
#import Queue
import random
import signal
import threading
import hashlib

import pywikibot
from pywikibot.comms.eventstreams import site_rc_listener
from pywikibot.diff import PatchManager

from redis import Redis
from redisconfig import KEYSIGN


TIMEOUT = 60 # We expect at least one rc entry every minute


class TimeoutError(Exception):
    pass


def on_timeout(signum, frame):
    raise TimeoutError


class Controller():
    def __init__(self):
#        self.total = 20
        self.site = pywikibot.Site(user="SignBot")
        self.site.login()  # T153541
        self.useroptin = None
        self.useroptout = None
        self.excluderegex = None
        self.redis = Redis(host="tools-redis")

    @property
    def total(self):
        return 20

    @total.setter
    def set_total(self):
        pass

    def run(self):
        signal.signal(signal.SIGALRM, on_timeout)
        signal.alarm(TIMEOUT)

        rc = site_rc_listener(self.site)

        for change in rc:
            signal.alarm(TIMEOUT)

            # Talk page or project page, bot edits excluded
            if (not change['bot']) and (change['namespace'] == 4 or change['namespace'] % 2 == 1) and (change['type'] in ['edit', 'new']) and (not '!nosign!' in change['comment']):
                t = BotThread(self.site, change, self)
                t.start()

        pywikibot.log("Main thread exit - THIS SHOULD NOT HAPPEN")
        time.sleep(10)

    def checknotify(self, user):
        if user.isAnonymous(): return False
        reset = int(time.time()) + 86400
        key = KEYSIGN + ":" + hashlib.md5(user.username.encode('utf-8')).hexdigest()
        p = self.redis.pipeline()
        p.incr(key)
        p.expireat(key, reset + 10)
        return p.execute()[0] >= 3

class BotThread(threading.Thread):
    def __init__(self, site, change, controller):
        threading.Thread.__init__(self)
        self.site = site
        self.change = change
        self.controller = controller

    def run(self):
        self.page = pywikibot.Page(self.site, self.change['title'], ns=self.change['namespace'])
        self.output(u"Handling")
        if self.page.isRedirectPage():
            self.output(u"Redirect")
            return
        if self.page.namespace() == 4:
            # Project pages needs attention (__NEWSECTIONLINK__)
            if not self.isDiscussion(self.page):
                self.output(u"Not a discussion")
                return
        user = pywikibot.User(self.site, self.change['user'])
        if self.isOptout(user):
            self.output(u"%s opted-out" % user)
            return

        # diff-reading.
        if self.change['type'] == 'new':
            old_text = ''
        else:
            old_text = self.page.getOldVersion(self.change['revision']['old'])

        new_text = self.page.getOldVersion(self.change['revision']['new'])

        if "{{speedy" in new_text.lower():
            self.output(u"{{speedy -- ignored")
            return

        diff = PatchManager(old_text.split("\n") if old_text else [], new_text.split("\n"), by_letter=True)
        diff.print_hunks()

        tosignstr = False
        tosignnum = False

        for block in diff.blocks:
            if block[0] < 0: continue
            hunk = diff.hunks[block[0]]
            group = hunk.group

#            print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)" %
#                (block[0], block[1][0], block[1][1], hunk.a[block[1][0]:block[1][1]], block[2][0], block[2][1], hunk.b[block[2][0]:block[2][1]]))

            for tag, i1, i2, j1, j2 in group:
#                print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)" %
#                    (tag, i1, i2, hunk.a[i1:i2], j1, j2, hunk.b[j1:j2]))
                if tag == 'insert':
                    for j in range(j1, j2):
                        line = hunk.b[j]
                        if self.page == user.getUserTalkPage() or self.page.title().startswith(
                                user.getUserTalkPage().title() + '/'):
                            if "{{" in line.lower():
                               self.output(u"User adding templates to his own talk page -- ignored")
                               return

                        excluderegextest = self.matchExcludeRegex(line)
                        if excluderegextest is not None:
                            self.output(u"%s -- ignored" % excluderegextest)
                            return
                               
                        if self.isComment(line):
                            tosignnum = j
                            tosignstr = line
                            if self.isSigned(user, tosignstr):
                                self.output(u"Signed")
                                return
                        
        if tosignstr is False:
            self.output(u"No inserts")
            return
        if self.isSigned(user, tosignstr):
            self.output(u"Signed")
            return

        if not self.isFreqpage(self.page):
            self.output(u"Waiting")
            time.sleep(60)
            pass

        currenttext = self.page.get(force=True).split("\n")
        if currenttext[tosignnum] == tosignstr:
            currenttext[tosignnum] += self.getSignature(tosignstr, user)
        elif currenttext.count(tosignstr) == 1:
            currenttext[currenttext.index(tosignstr)] += self.getSignature(tosignstr, user)
        else:
            self.output(u"Line no longer found, probably signed")
            return
        
        summary = u'Signing comment by %s - "%s"' % (self.userlink(user), self.change['comment'])
        
        self.userPut(self.page, self.page.get(), u"\n".join(currenttext), comment=summary)

        # self.notify(user) {{subst:Please sign}} -- ignore {{bots}}
        if self.controller.checknotify(user):
            self.output(u"Notifying %s" % user)
            talk = user.getUserTalkPage()
            if talk.isRedirectPage(): talk = talk.getRedirectTarget()
            try:
                talktext = talk.get(force=True, get_redirect=True) + u'\n\n'
            except pywikibot.NoPage:
                talktext = ''

            talktext += u'{{subst:Please sign}} --~~~~'
            self.userPut(talk, talk.text, talktext, comment=u"Added {{subst:[[Template:Please sign|Please sign]]}} note.", minor=False)

    def output(self, info):
        pywikibot.output(u"%s: %s" % (self.page, info))

    def getSignature(self, tosignstr, user):
        p = u""
        if tosignstr[-1] != " ": p = u" "
        timestamp = pywikibot.Timestamp.utcfromtimestamp(self.change['timestamp']).strftime('%H:%M, %-d %B %Y')
#        return p + u"{{%s|%s|%s}}" % ("unsignedIP" if user.isAnonymous() else "unsigned", user.username, timestamp)
        return p + u"{{%s|%s|%s}}" % ("unsignedIP2" if user.isAnonymous() else "unsigned2", timestamp, user.username)

    def userlink(self, user):
        if user.isAnonymous():
            return u"[[Special:Contributions/%s|%s]]" % (user.username, user.username)
        else:
            return u"[[User:%s|%s]]" % (user.username, user.username)

    def isSigned(self, user, tosignstr):
        for wikilink in pywikibot.link_regex.finditer(pywikibot.textlib.removeDisabledParts(tosignstr)):
            if not wikilink.group("title").strip(): continue
            try:
                link = pywikibot.Link(wikilink.group("title"), source=self.site)
                link.parse()
#            except (pywikibot.InvalidTitle, pywikibot.SiteDefinitionError):
            except pywikibot.Error:
                continue
#            if link.site != self.site: continue
            if user.isAnonymous():
                if link.namespace != -1: continue
                if link.title != u"Contributions/" + user.username: continue
            else:
                if link.namespace not in [2, 3]: continue
                if link.title != user.username: continue
            return True
                                                                                                
        return False

    def isComment(self, line):
        tempstr = re.sub(ur'\[\[[Cc]ategory:[^\]]+\]\]', '', pywikibot.textlib.removeDisabledParts(line).strip()) # remove non-functional parts and categories
        if not tempstr: return False # not empty
        if tempstr.startswith('=') and tempstr.endswith('='): return False # not heading
        if tempstr.startswith('|') or tempstr.startswith('{|') or tempstr.endswith('|'): return False # not table/template
        if tempstr.startswith('----'): return False # not horzontal line
        if re.match(ur'^__[A-Z]+__$', tempstr): return False # not magic words   

        return True

    @staticmethod
    def chance(c):
        return random.random() < c

    def isOptout(self, user):
        # 0.25 chance of updating list
        if self.controller.useroptin is None or self.controller.useroptout is None or self.chance(0.25):
            self.controller.useroptin = list(pywikibot.Page(self.site, "Template:YesAutosign").getReferences(onlyTemplateInclusion=True))
            self.controller.useroptout = list(pywikibot.Page(self.site, "Template:NoAutosign").getReferences(onlyTemplateInclusion=True))

        # Check for opt-in {{YesAutosign}} -> False
        if user in self.controller.useroptin: return False
        # Check for opt-out {{NoAutosign}} -> True
        if user in self.controller.useroptout: return True
        # Check for 800 user edits -> False
        # -> True
        return user.editCount(force=self.chance(0.25)) > 800

    def isFreqpage(self, page):
        # TODO
        # 0.25 chance of updating list
        return False

    def isDiscussion(self, page):
        # TODO: sandbox
        # TODO: opt-in
        # 0.25 chance of updating list
        return "newsectionlink" in self.page.properties()

    def matchExcludeRegex(self, line):
        # 0.05 chance of updating list
        if self.controller.excluderegex is None or self.chance(0.05):
            # We do not directly assign to self.controller.excluderegex right now to avoid issues with multi-threading
            lst  = []

            repage = pywikibot.Page(self.site, "User:SignBot/exclude_regex")
            for line in repage.get(force=True).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    lst.append(re.compile(line, re.I))

            self.controller.excluderegex = lst

	line = line.replace('_', ' ')
        for regex in self.controller.excluderegex:
            reobj = regex.search(line)
            if reobj is not None:
                return reobj.group(0)
        return None

    def userPut(self, page, oldtext, newtext, **kwargs):
        if oldtext == newtext:
            pywikibot.output(u'No changes were needed on %s'
                             % page.title(asLink=True))
            return
#        elif self.controller.total <= 0:
#            raise RuntimeError("Maxium edits reached!")
        else:
            self.controller.total -= 1

        pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                         % page.title(asLink=True))
#        if self.simulate:
        if True:
            pywikibot.showDiff(oldtext, newtext)
            if 'comment' in kwargs:
                pywikibot.output(u'Comment: %s' % kwargs['comment'])

#            return

        page.text = newtext
        try:
            page.save(**kwargs)
            pass
        except pywikibot.Error, e:
            pywikibot.output(u'Failed to save %s: %r: %s' % (page.title(asLink=True), e, e))
            self.controller.total += 1

def main():
    pywikibot.handleArgs()

    Controller().run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
