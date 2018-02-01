import logging
import threading
import sleekxmpp

from sleekxmpp.jid import JID
from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.plugins import BasePlugin, register_plugin
from sleekxmpp.stanza.roster import Roster, RosterItem

logging.basicConfig(level=logging.DEBUG)


class Bot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(Bot, self).__init__(jid, password)

        # We'll limit roster approvals to a whitelisted set
        self.auto_authorize = None
        self.auto_subscribe = None
        self.whitelisted_contacts= set()
        try:
            with open('data/whitelist.txt', 'r+') as whitelist:
                for jid in whitelist:
                    jid = jid.strip()
                    if jid:
                        self.whitelisted_contacts.add(JID(jid))
        except IOError:
            logging.debug('Could not load whitelist')


        self.whitespace_keepalive = True

        self.register_plugin('xep_0012')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0050')
        self.register_plugin('xep_0054')
        self.register_plugin('xep_0084')
        self.register_plugin('xep_0085')
        self.register_plugin('xep_0092')
        self.register_plugin('xep_0106')
        self.register_plugin('xep_0107')
        self.register_plugin('xep_0108')
        self.register_plugin('xep_0115')
        self.register_plugin('xep_0153')
        self.register_plugin('xep_0172')
        self.register_plugin('xep_0184')
        self.register_plugin('xep_0198')
        self.register_plugin('xep_0199', {'keepalive': True})
        self.register_plugin('xep_0202')
        self.register_plugin('xep_0308')

        self['xep_0092'].software_name = 'SleekXMPP Bot Example'
        self['xep_0092'].version = '1.0'

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.echo)
        self.add_event_handler('roster_subscription_request',
                self.roster_subscription_request)
        self.add_event_handler('custom_event', self.custom_event)

    def session_start(self, event):
        self.get_roster()
        self.send_presence()

        self['xep_0012'].set_last_activity(seconds=0)
        self['xep_0172'].publish_nick('Example Sleek Bot')
        self['xep_0108'].publish_activity('working')
        self['xep_0107'].publish_mood('excited')

        vcard = self['xep_0054'].stanza.VCardTemp()
        vcard['FN'] = 'Example Bot'
        vcard['NICKNAME'] = 'Example Bot'
        vcard['JABBERID'] = self.boundjid.bare
        vcard['ORG']['ORGNAME'] = 'Bots Inc'
        vcard['URL'] = 'http://example.com/myhomepage'
        vcard['DESC'] = "I'm a bot!"
        self['xep_0054'].publish_vcard(vcard)

        avatar_data = None
        try:
            with open('data/avatar.png', 'rb') as avatar_file:
                avatar_data = avatar_file.read()
        except IOError:
            logging.debug('Could not load avatar')
        if avatar_data:
            avatar_id = self['xep_0084'].generate_id(avatar_data)
            info = {
                'id': avatar_id,
                'type': 'image/png',
                'bytes': len(avatar_data)
            }
            self['xep_0084'].publish_avatar(avatar_data)
            self['xep_0084'].publish_avatar_metadata(items=[info])
            self['xep_0153'].set_avatar(avatar=avatar_data, mtype='image/png')

    def roster_subscription_request(self, pres):
        if pres['from'].bare in self.whitelisted_contacts:
            self.send_presence(pto=pres['from'], ptype='subscribed')
            if self.client_roster[pres['from']]['subscription'] != 'both':
                self.send_presence(pto=pres['from'], ptype='subscribe')
            self.client_roster.send_last_presence()
        else:
            self.send_presence(pto=pres['from'], ptype='unsubscribed')

    def echo(self, msg):
        # Ignore anything from ourself
        if msg['from'].bare == self.boundjid.bare:
            return

        if msg['type'] in ('chat', 'normal'):
            mfrom, orig = msg['from'], msg['body']
            msg.reply()
            msg['body'] = 'You sent: %s' % orig
            try:
                if self['xep_0030'].supports(mfrom, feature='http://jabber.org/protocol/xhtml-im'):
                    # For now, you can only include one outer element. So wrap in a <div /> if needed.
                    msg['html']['body'] = '<p><b>You sent:</b> %s</p>' % orig
            except XMPPError:
                pass
            msg.send()

    def custom_event(self, data):
        for jid in self.client_roster:
            m = self.Message()
            m['to'] = jid
            m['body'] = 'Custom event: %s' % data
            m.send()


if __name__ == '__main__':
    b = Bot('yourbot@example.com', 'secret')
    b.connect()
    b.process(block=False)
