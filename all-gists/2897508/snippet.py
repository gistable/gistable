class ConnectionHandler(SockJSConnection):
    def __init__(self, *args, **kwargs):
        super(ConnectionHandler, self).__init__(*args, **kwargs)
        self.client = brukva.Client()
        self.client.connect()
        self.client.subscribe('some_channel')

    def on_open(self, info):
        self.client.listen(self.on_chan_message)

    def on_message(self, msg):
        # this is a message broadcast from the client
        # handle it as necessary (this implementation ignores them)
        pass

    def on_chan_message(self, msg):
        # this is a message received from redis
        # send it to the client
        self.send(msg.body)

    def on_close(self):
        self.client.unsubscribe('text_stream')
        self.client.disconnect()
