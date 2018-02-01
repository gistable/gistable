class XMPPHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message):
        idx  = message.sender.index('/')
        user = message.sender[0:idx]
        logging.debug(user)