class TileServer(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):
        """
        In addition to invoking the superclass constructor, initializes the per-server redis client and per-server
        redis pubsub handler.
        """
        tornado.web.Application.__init__(self, handlers, default_host, transforms, wsgi, **settings)
        self._rc = redis.StrictRedis(**(settings.get('redis_config', {})))  # redis client: one per application
        self._rcps = self._rc.pubsub()                                      # redis pubsub obj: one per application
        self._sub_cbs = {}                                                  # redis pubsub callbacks: one per subscription
        self._sub_cmd_q = 'q_sub_cmds_' + uuid4().hex # TODO: could make a shorter ID just based on tornado server ID
        self._rcps.subscribe(self._sub_cmd_q)
        listener = threading.Thread(target=self._rc_listen)
        listener.setDaemon(True)
        listener.start()

    def sub_user_feed(self, feed_id, callback):
        """
        Subscribes the callback for updates to the user's feed.
        feed_id: a unique identifier for the feed.  For registered users, it makes sense for this
        to be the same as the user id.  For non-registered users, it's arbitrary but
        must be unique across all users.
        """
        self._subscribe('q_user_' + str(feed_id), callback)

    def unsub_user_feed(self, feed_id, callback):
        self._unsubscribe('q_user_' + str(feed_id), callback)

    def pub_user_feed(self, feed_id, data):
        self._rc.publish('q_user_' + str(feed_id), data)

    def _subscribe(self, channel, callback):
        """
        Only channel subscriptions are supported, not pattern subs.
        Callback should take one argument, which is the received message data.
        Creating the subscription is a blocking call to the redis client.  That is, this call will block until
        the subscription is registered; it will _not_ block waiting for messages on the subscribed channel.
        """
        local_subs = self._sub_cbs.get(channel, None)
        if local_subs is None:
            local_subs = {callback}
            self._sub_cbs[channel]= local_subs
            self._rc.publish(self._sub_cmd_q, 'subscribe:' + channel)
        else:
            local_subs.add(callback)

    def _unsubscribe(self, channel, callback):
        local_subs = self._sub_cbs.get(channel,None)
        if local_subs is not None:
            local_subs.remove(callback)
            if not len(local_subs):
                self._rc.publish(self._sub_cmd_q, 'unsubscribe:' + channel)
                del self._sub_cbs[channel]

    def _process_msg(self, msg):
        channel = msg['channel']
        data = msg['data']
        if channel == self._sub_cmd_q:
            command = data.split(':')
            if command[0] == 'subscribe':
                result = self._rcps.subscribe(command[1])
            elif command[0] == 'unsubscribe':
                result = self._rcps.unsubscribe(command[1])
            if type(result) == list and result[0] == 'message':  # Kludge to avoid race condition in redis-py pubsub
                self._process_msg({
                    'type': result[0],
                    'pattern': None,
                    'channel': result[1],
                    'data': result[2]
                })
        elif msg.get('type', None) == 'subscribe' or msg.get('type') == 'unsubscribe':
            pass # Kludge because sometimes redis-py will treat the return value from a UN/SUBSCRIBE call as a message.
        else:
            listeners = self._sub_cbs.get(channel,[])
            for listener in listeners: IOLoop.instance().add_callback(functools.partial(listener, data))

    def _rc_listen(self):
        for msg in self._rcps.listen():
            try:
                self._process_msg(msg)
            except Exception as msg_failure:
                logger.warn("Could not process message: %r" % msg)
                logger.warn("Error: %r" % msg_failure)
