# -*- coding: utf-8 -*- 

# The MIT License (MIT)
# 
# Copyright (c) 2013 Craften.de Team
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import willie.module
import re
import datetime

STATUS_OK = 0
STATUS_WAITING = 1
STATUS_IDLE = 2

available_supporters = {}
open_tickets = {}
closed_tickets = 0
next_ticket = 0

class config:
    """
    A simple struct for providing the options of this module. 
    Contains default values as static attributes.
    """
    channel = '#callcenter'
    supporters = []
    ticket_idle = 30  # ticket is idle after 30 seconds
    ticket_timeout = 300  # ticket times out after 5 minutes
    supporter_idle = 120  # supporter is idle after 2 minutes
    supporter_timeout = 600  # supporter times out after 10 minutes 
    supporter_askifaliveinterval = 30  # asks idle supporters if they are still alive every 30 seconds
    msg_no_supporter = 'We are sorry but there are no supporters online. We will notify you when someone is here!'
    msg_invalid_ticket = 'Sorry, you have no valid support ticket. Please start a new direct support session!'
    msg_idle_closed = "We closed your support ticket because you didn't say anything for a while."
    msg_after_support = "We hope we were able to help you! :-)"
    msg_supporter_available = "A supporter is now available!"
    pass

class Ticket:
    def __init__(self, nickname, language):
        self.nickname = nickname
        self.language = language
        self.lasttime = datetime.datetime.now()
        self.status = STATUS_OK
    def touch(self):
        """
        Markiert dieses Ticket als aktiv und setzt die Zeit zurück
        """
        self.lasttime = datetime.datetime.now()
        self.status = STATUS_OK
    def is_with(self, nickname):
        return self.nickname.lower() == nickname.lower()
    @staticmethod
    def by_nick(nick):
        global open_tickets
        for k in open_tickets:
            if open_tickets[k].is_with(nick):
                return k
        return None
    def get_idletime(self):
        """
        Returns since how many seconds this ticket is idle.
        """
        return (datetime.datetime.now() - self.lasttime).total_seconds()
        
    
class OnlineSupporter:
    def __init__(self, nickname):
        self.nickname = nickname
        self.lasttime = datetime.datetime.now()
        self.lastaskalivetime = 0
    def touch(self):
        self.lasttime = datetime.datetime.now()  
    def get_idletime(self):
        return (datetime.datetime.now() - self.lasttime).total_seconds()
    def may_askifalive(self):
        return (datetime.datetime.now() - self.lastaskalivetime).total_seconds() >= config.supporter_askifaliveinterval;

def open_ticket(nick):
    global next_ticket
    ticket = next_ticket
    open_tickets[ticket] = Ticket(nick[0], nick[1])
    next_ticket += 1
    return ticket;

def close_ticket(ticket, is_done=True):
    if ticket in open_tickets:
        open_tickets.pop(ticket)
        if is_done:
            global closed_tickets
            closed_tickets += 1
        return True
    else:
        return False

def get_nick_by_ticket(ticket):
    if ticket in open_tickets:
        return open_tickets[ticket].nickname
    else:
        return None

def get_ticket_stats():
    return mirc_format("^B^K07%d^R tickets open (^B^K14+%d^R idle), ^B^K10%d^R tickets done" % (
                        sum(open_tickets[s].status == STATUS_OK for s in open_tickets),
                        sum(open_tickets[s].status == STATUS_IDLE for s in open_tickets),
                        closed_tickets))

@willie.module.event('PRIVMSG')
@willie.module.rule('.*')
def forward(bot, trigger):
    if trigger.sender == trigger.nick:
        # Es ist eine Query, weil Quelle==Nickname statt Quelle==Channelname
        ticket = Ticket.by_nick(trigger.nick);
        if ticket != None:
            bot.msg(config.channel, mirc_format("^K4%s ^K4,15#%d^K^K4:^K %s" % (str(trigger.nick), ticket, trigger.bytes)))
            open_tickets[ticket].touch()
        else:
            m = re.match(r"HELP:(.+);(.*)", trigger.bytes)
            if (m):
                ticket = open_ticket((trigger.nick, m.groups(1)))
                bot.msg(config.channel, mirc_format("^K4New ticket: ^K4,15#%d^K^K4 (%s, %s)" % (ticket, trigger.nick, m.group(1))))
                if len(available_supporters) == 0:
                    open_tickets[ticket].status = STATUS_WAITING;
                    bot.msg(trigger.nick, config.msg_no_supporter)
            else:
                bot.msg(trigger.nick, config.msg_invalid_ticket)
    elif trigger.sender == config.channel and trigger.nick.lower() in config.supporters:
        # Es ist eine Nachricht im Support-Channel. Cool!
        # Lebenszeichen des Supporters eintragen
        m = re.match(r"(\d+) (.*)$", trigger.bytes)
        if m:
            supporter_as_online(bot, trigger.nick)
            target = get_nick_by_ticket(int(m.group(1)))
            if target is not None:
                bot.msg(target, m.group(2))
        
        if available_supporters.has_key(trigger.nick.lower()):
            if available_supporters[trigger.nick.lower()].get_idletime() > config.supporter_idle:
                bot.write(('NOTICE', trigger.nick), "Hey %s, glad you're still here!" % trigger.nick)
                bot.msg(config.channel, get_ticket_stats())
            available_supporters[trigger.nick.lower()].touch()

@willie.module.commands('stats')
def show_stats(bot, trigger):
    bot.msg(config.channel, get_ticket_stats())

@willie.module.rule(r'(?i)done (\d+)$')
@willie.module.commands('done')
def mark_ticket_done(bot, trigger):
    if trigger.sender == config.channel and trigger.nick.lower() in config.supporters:
        supporter_as_online(bot, trigger.nick)
        ticket = int(trigger.group(2))
        target = get_nick_by_ticket(ticket)
        if close_ticket(ticket):
            bot.msg(config.channel, get_ticket_stats())
            bot.msg(target, config.msg_after_support);

def supporter_as_online(bot, nick):
    """
    Marks a supporter as online
    """
    if nick.lower() in config.supporters and not nick.lower() in available_supporters:
        available_supporters[nick.lower()] = OnlineSupporter(nick)
        bot.msg(config.channel, "%s just logged in!" % nick)
        for k in open_tickets.copy():
            if open_tickets[k].status == STATUS_WAITING:
                bot.msg(open_tickets[k].nickname, config.msg_supporter_available)
                open_tickets[k].touch()
        bot.msg(config.channel, get_ticket_stats())

@willie.module.commands('me')
def supporter_joins(bot, trigger):
    if trigger.group(2) == 'on':
        supporter_as_online(bot, trigger.nick)
    elif trigger.group(2) == 'off':
        if supporter_quit(trigger.nick):
            bot.msg(config.channel, "Allright %s, you've done enough for today!" % trigger.nick)
      
def supporter_quit(nick):
    """
    Removes a supporter from the list of available supporters.
    Returns false if that supporter was not on the list.
    """
    if available_supporters.has_key(nick.lower()):
            available_supporters.pop(nick.lower())
            return True
    return False
      
@willie.module.interval(10)
def check_heartbeat(bot):
    # I. Um abwesende Supporter kuemmern
    for k in available_supporters.copy():
        if available_supporters[k].get_idletime() > config.supporter_timeout:
            if supporter_quit(k):
                bot.msg(config.channel, '%s is not available for support anymore.' % k)
        elif available_supporters[k].get_idletime() > config.supporter_idle and available_supporters[k].may_askifalive:
            bot.write(('NOTICE', k), '%s, are you still alive?' % k)
            available_supporters[k].lastaskalivetime = datetime.datetime.now()
    # II. Um abwesende Tickets kuemmern
    for k in open_tickets.copy():
        if open_tickets[k].get_idletime() > config.ticket_timeout:
            bot.msg(open_tickets[k].nickname, config.msg_idle_closed)
            if close_ticket(k, False):
                bot.msg(config.channel, "Closed idle ticket #%d." % k)
        elif open_tickets[k].get_idletime() > config.ticket_idle:
            open_tickets[k].status = STATUS_IDLE
           
def setup(bot):
    for attr, value in config.__dict__.iteritems():
        if not attr.startswith('__'):
            if bot.config.has_option('supportbot', attr):
                valueToUse = getattr(bot.config.supportbot, attr);
                print type(value)
                if isinstance(value, int):
                    valueToUse = int(valueToUse)
                elif isinstance(value, list):
                    valueToUse = valueToUse.lower().split(',')
                setattr(config, attr, valueToUse)
            else:
                bot.debug('SupportCenter', '%s is missing, will use "%s"' % (attr, value), 'warning')

def configure(botconfig):
    if botconfig.option("Configure the Support Center"):
        botconfig.add_section('supportbot')
        botconfig.interactive_add('supportbot', 'channel', 'In which channel will the supporters work? (The bot must be in that channel!)', config.channel)
        botconfig.add_list('supportbot', 'supporters', 'Enter all supporters!', 'Nickname:')
        botconfig.interactive_add('supportbot', 'ticket_idle', 'After how many seconds should a ticket be marked as inactive?', config.ticket_idle)
        botconfig.interactive_add('supportbot', 'ticket_timeout', 'After how many seconds of inactivity should a ticket be deleted?', config.ticket_timeout)
        botconfig.interactive_add('supportbot', 'supporter_idle', 'After how many seconds should a supporter be asked if he is alive?', config.supporter_idle)
        botconfig.interactive_add('supportbot', 'supporter_timeout', 'After how many seconds of inactivity should a supporter be marked as offline?', config.supporter_timeout)
        botconfig.interactive_add('supportbot', 'supporter_askifaliveinterval', 'How often should an idle supporter be asked if he is alive? (Interval in seconds)', config.supporter_askifaliveinterval)
        
def mirc_format(s):
    """ 
    Replaces mIRC-Codes (for example ^K for Strg+K for colors) with the corresponding chars 
    """
    s = s.replace("^B", chr(0x02))
    s = s.replace("^K", chr(0x03))
    s = s.replace("^R", chr(0x0f))
    return s;