import logging
import threading
import sleekxmpp


logging.basicConfig(level=logging.DEBUG)

class Bot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(Bot, self).__init__(jid, password)
        
        self.ready = threading.Event()

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0066') # OOB
        self.register_plugin('xep_0231') # BOB

        self.add_event_handler('session_start', self.session_start)

    def session_start(self, event):
        self.get_roster()
        self.send_presence()
        self.ready.set()

    def send_image_html(self, jid, img_url):
        m = self.Message()
        m['to'] = jid
        m['type'] = 'chat'
        m['body'] = 'Tried sending an image using HTML-IM'
        m['html']['body'] = '<img src="%s" />' % img_url
        m.send()

    def send_image_bob(self, jid, img_file_path):
        m = self.Message()
        m['to'] = jid
        m['type'] = 'chat'
        with open(img_file_path, 'rb') as img_file:
            img = img_file.read()
        if img:
            cid = self['xep_0231'].set_bob(img, 'image/png')
            m['body'] = 'Tried sending an image using HTML-IM + BOB'
            m['html']['body'] = '<img src="cid:%s" />' % cid
            m.send()

    def send_image_oob(self, jid, img_url):
        m = self.Message()
        m['to'] = jid
        m['type'] = 'chat'
        m['body'] = 'Tried sending an image using OOB'
        m['oob']['url'] = img_url
        m.send()


if __name__ == '__main__':
    b = Bot('bot@example.com', 'secret')
    b.connect()
    b.process(block=False)
    b.ready.wait()

    b.send_image_html('someone@example.com', 'http://example.com/image.png')
    b.send_image_bob('someone@example.com', 'image.png')
    b.send_image_oob('someone@example.com', 'http://example.com/image.png')
