#!/usr/bin/python
import datetime
import logging
import threading
import weakref

import tornado
import tornado.gen
import pika

'''
Pika-Tornado: a Tornado coroutine-based abstraction layer for Pika.
'''

# (C) 2015 Stuart Longland <stuartl@longlandclan.yi.org>
# Released under the terms of the Mozilla Public License v2.0

class AMQPObject(object):
    @classmethod
    def _get_log(cls, *name):
        return logging.getLogger('.'.join(
            (cls.__module__, cls.__name__) + name))

class AMQPConnection(AMQPObject):
    '''
    Connection to AMQP, this object handles unexpected disconnections (and
    re-connects accordingly) and wraps the channel opening process in a
    coroutine-friendly manner.

    Support for multiple IOLoops is provided and thread-safety is attempted.

    Callbacks may be specified in a number of ways:
    - as a reference to the function directly
    - as a tuple:
        - first element gives the IOLoop (or None for the client's IOLoop)
        - second element gives the reference to the function
        - third element if present gives the initial args
        - forth element if present gives the initial kwargs
    '''

    CONNECTION_CLOSED   = pika.connection.Connection.CONNECTION_CLOSED
    CONNECTION_INIT     = pika.connection.Connection.CONNECTION_INIT
    CONNECTION_PROTOCOL = pika.connection.Connection.CONNECTION_PROTOCOL
    CONNECTION_START    = pika.connection.Connection.CONNECTION_START
    CONNECTION_TUNE     = pika.connection.Connection.CONNECTION_TUNE
    CONNECTION_OPEN     = pika.connection.Connection.CONNECTION_OPEN
    CONNECTION_CLOSING  = pika.connection.Connection.CONNECTION_CLOSING

    def __init__(self, parameters, on_open_callback=None,
            on_open_error_callback=None, on_close_callback=None,
            on_giveup_callback=None, reconnect_delay=5.0, reconnect_max=-1,
            io_loop=None, io_thread=None):

        '''
        Initialise a connection to AMQP.

        :param: pika.connection.Parameters parameters:
            Connection parameters, see Pika documentation.

        :param method on_open_callback:
            Called when the connection is opened.

        :param method on_open_error_callback:
            Called if the connection can't be opened.

        :param method on_close_callback:
            Called when the connection is closed.

        :param method on_giveup_callback:
            Called when the connection attempts have been exhausted
            and this library "gives up".  This might be used to log
            an alarm and shut down the daemon.

        :param float reconnect_delay:
            The amount of time to wait before attempting to reconnect.
            Set to 0 to disable reconnect.

        :param int reconnect_max:
            The maximum number of reconnection attempts.  Set to 0 to
            permit unlimited reconnections.

        :param tornado.ioloop.IOLoop io_loop:
            IOLoop instance to use for the AMQP client itself.  By default,
            the current IOLoop is used.

        :param threading.Thread io_thread:
            Thread used for AMQP communications.  Since Pika itself is not
            thread-safe, it is imperative that all AMQP operations take place
            in the same thread as the AMQP IOLoop instance.

            If this is different to the thread the constructor is running in
            for whatever reason, the reference to that thread can be given
            here.
        '''

        if io_loop is None:
            io_loop     = tornado.ioloop.IOLoop.current()
        if io_thread is None:
            io_thread   = threading.current_thread()

        self._io_loop           = io_loop
        self._io_thread         = io_thread
        self._reconnect_delay   = datetime.timedelta(seconds=reconnect_delay)
        self._reconnect_max     = reconnect_max
        self._reconnect_rem     = reconnect_max
        self._reconnect         = reconnect_delay > 0
        self._giveup            = False

        self._on_open_cb        = []
        self._on_open_error_cb  = []
        self._on_close_cb       = []
        self._on_giveup_cb      = []
        if on_open_callback is not None:
            self._on_open_cb.append(
                    self._get_callback(on_open_callback))
        if on_open_error_callback is not None:
            self._on_open_error_cb.append(
                    self._get_callback(on_open_error_callback))
        if on_close_callback is not None:
            self._on_close_cb.append(
                    self._get_callback(on_close_callback))
        if on_giveup_callback is not None:
            self._on_giveup_cb.append(
                    self._get_callback(on_giveup_callback))

        self._amqp_parameters   = parameters
        self._amqp_connection   = None
        self._channels          = []
        self._replace_connection()

    # ------------------------------------------------------------------------
    # Connection state
    # ------------------------------------------------------------------------

    connection_state    = property(lambda s : \
            s._amqp_connection.connection_state)
    is_closed           = property(lambda s : s._amqp_connection.is_closed)
    is_closing          = property(lambda s : s._amqp_connection.is_closing)
    is_open             = property(lambda s : s._amqp_connection.is_open)

    # ------------------------------------------------------------------------
    # Connection callbacks
    # ------------------------------------------------------------------------

    def add_on_open_callback(self, callback, callback_args=None,
            callback_kwargs=None):
        self._on_open_cb.append(
                self._get_callback(callback, callback_args, callback_kwargs))

    def add_on_open_error_callback(self, callback, callback_args=None,
            callback_kwargs=None):
        self._on_open_error_cb.append(
                self._get_callback(callback, callback_args, callback_kwargs))

    def add_on_close_callback(self, callback, callback_args=None,
            callback_kwargs=None):
        self._on_close_cb.append(
                self._get_callback(callback, callback_args, callback_kwargs))

    def add_on_giveup_callback(self, callback, callback_args=None,
            callback_kwargs=None):
        self._on_giveup.append(
                self._get_callback(callback, callback_args, callback_kwargs))

    # ------------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------------

    def _replace_connection(self):
        log      = self._get_log('_replace_connection')
        try:
            log.debug('Gathering a list of existing channels')
            # Grab a list of channels
            channels = self._get_channels()
            log.debug(  'We have %s channels to reopen.  Opening '\
                        'connection to AMQP with parameters %s.',
                        len(channels), self._amqp_parameters)

            # Replace the connection
            self._amqp_connection   = pika.adapters.TornadoConnection(
                parameters              = self._amqp_parameters,
                on_open_callback        = self._handle_on_open_callback,
                on_open_error_callback  = self._handle_on_open_error_callback,
                on_close_callback       = self._handle_on_close_callback,
                custom_ioloop           = self._io_loop)
            log.debug('AMQP connection started')

            # Mark these channels as stale
            for ch in channels:
                try:
                    log.debug('Re-opening %s', ch)
                    ch._mark_stale()
                except:
                    pass
        except:
            log.exception('Failed to replace connection')

    def connect(self, timeout=None):
        '''
        Connect to AMQP.
        '''
        return self._run_async(
                self._amqp_connection.connect,
                (),
                {},
                timeout,
                None,
                None)

    def close(self, *args, **kwargs):
        '''
        Disconnect from AMQP.  This disables reconnections.
        See pika.BaseConnection.close for details on arguments.
        '''
        timeout         = kwargs.pop('timeout',None)
        self._giveup    = False
        self._reconnect = False
        return self._run_async(
                async_func  = self._amqp_connection.close,
                args        = args,
                kwargs      = kwargs,
                timeout     = timeout,
                cb_func     = None,
                future      = None)

    def set_backpressure_multiplier(self, *args, **kwargs):
        return self._run_async(
                async_func  = self._amqp_connection.set_backpressure_multiplier,
                args        = args,
                kwargs      = kwargs,
                timeout     = timeout,
                cb_func     = None,
                future      = None)

    # ------------------------------------------------------------------------
    # Connection callbacks
    # ------------------------------------------------------------------------

    def add_backpressure_callback(self, callback):
        return self._run_async(
                self._amqp_connection.add_backpressure_callback,
                    args=(self._get_callback(callback),))

    def add_on_close_callback(self, callback):
        return self._run_async(
                self._amqp_connection.add_on_close_callback,
                    args=(self._get_callback(callback),))

    def add_on_open_callback(self, callback):
        return self._run_async(
                self._amqp_connection.add_on_open_callback,
                    args=(self._get_callback(callback),))

    def add_on_open_error_callback(self, callback):
        return self._run_async(
                self._amqp_connection.add_on_open_error_callback,
                    args=(self._get_callback(callback),))

    # ------------------------------------------------------------------------
    # Channel management
    # ------------------------------------------------------------------------

    def _cleanup_channels(self):
        self._channels  = filter(lambda cr : cr() is not None, self._channels)

    def _get_channels(self):
        self._cleanup_channels()
        return [ch() for ch in self._channels]

    @tornado.gen.coroutine
    def channel(self, channel_number=None, timeout=None):
        '''
        Open a new channel on the AMQP connection.
        '''
        ch = AMQPChannel(self, channel_number)
        yield ch._init_channel(timeout)
        self._cleanup_channels()
        self._channels.append(weakref.ref(ch))
        raise tornado.gen.Return(ch)

    # ------------------------------------------------------------------------
    # Connection handling callbacks
    # ------------------------------------------------------------------------

    def _handle_on_open_callback(self, *args, **kwargs):
        '''
        What to do when the connection is opened?
        '''
        log = self._get_log('_handle_on_open_callback')
        try:
            log.info('Connection open')
            self._reconnect     = self._reconnect_delay.total_seconds() > 0
            self._reconnect_rem = self._reconnect_max
            self._giveup        = False

            # Grab a list of channels
            channels = self._get_channels()
            # Re-open those channels
            for ch in channels:
                log.debug('Re-opening %s', ch)
                yield ch._init_channel()

            log.debug('Calling open callbacks')
            for cb in self._on_open_cb:
                self._io_loop.add_callback(cb, *args, **kwargs)
        except:
            log.exception('Failed to handle connection open')

    def _handle_on_close_callback(self, *args, **kwargs):
        '''
        What to do when the connection is closed?
        '''
        log = self._get_log('_handle_on_close_callback')
        try:
            log.info('Connection closed')
            for cb in self._on_close_cb:
                try:
                    cb(*args, **kwargs)
                except:
                    log.exception('Exception in callback %s(*%s, **%s)',
                            cb, args, kwargs)
        except:
            log.exception('Exception in close callback')
        self._reconnect()

    def _handle_on_open_error_callback(self, connection, error,
                *args, **kwargs):
        '''
        What to do if we fail to open the connection?
        '''
        log = self._get_log('_handle_on_open_error_callback')
        try:
            log.error('Received %s whilst attempting connection', error)

            # Pass it through to the callback handler we were given
            if self._on_open_error_cb is not None:
                for cb in self._on_open_error_cb:
                    try:
                        cb(connection, error, *args, **kwargs)
                    except:
                        log.exception('Error in callback %s(*%s, **%s)',
                                cb, args, kwargs)
        except:
            log.exception('Failed in open-error callback')
        self._reconnect()

    def _reconnect(self):
        '''
        Perform a re-connection, if enabled.
        '''
        log = self._get_log('_reconnect')
        try:
            # Sanity check, ensure we're running in the correct thread for this.
            # add_timeout is *NOT* thread-safe.
            if not self._is_own_thread:
                # This should do the trick!
                self._io_loop.add_callback(_reconnect)
                return

            # Reconnect?
            if self._reconnect:
                if self._reconnect_max > 0:
                    self._reconnect_rem -= 1
                    self._reconnect = self._reconnect_rem > 0
                    self._giveup = not self._reconnect
                    if self._giveup:
                        log.error('This is our last connection attempt!')

                # Schedule a reconnect.  We do this by completely replacing the
                # AMQP connection object.
                self._io_loop.add_timeout(
                        self._reconnect_delay, self._replace_connection)
                log.error('Re-connecting in %s.',
                        self._reconnect_delay)
            elif self._giveup:
                log.fatal('Giving up!')
                for cb in self._on_giveup_cb:
                    try:
                        cb()
                    except:
                        log.exception('Exception in callback %s', cb)
        except:
            log.exception('Failure in recnnection')

    # ------------------------------------------------------------------------
    # Callback and thread-safety utilities
    # ------------------------------------------------------------------------

    @property
    def _is_own_thread(self):
        '''
        Return True if we're running in our own thread.
        '''
        return self._io_thread is threading.current_thread()

    def _schedule_timeout(self, timeout, future, cb_func=None,
            cb_args=None, cb_kwargs=None):
        '''
        Place a TimeoutException into the future if the future is not
        completed in time.
        '''
        assert self._is_own_thread, 'This isn\'t my thread!'
        if cb_args is None:
            cb_args = ()
        if cb_kwargs is None:
            cb_kwargs = {}

        def _timeout():
            if not future.done():
                future.set_exception(TimeoutError())
            if cb_func is not None:
                cb_func(*cb_args, **cb_kwargs)
        return self._io_loop.add_timeout(timeout, _timeout)
    
    @tornado.gen.coroutine
    def _run_async(self, async_func, args=None, kwargs=None, timeout=None,
            cb_func=None, callback_name='callback', future=None):
        '''
        Run a method in our own thread and return its result.

        args and kwargs are passed to async_func, which will be run in the
        AMQP IOLoop.

        timeout specifies a time limit on the operation, and will result in a
        TimeoutError if the operation does not complete.

        callback, if given, causes a callback keyword argument to be passed to
        async_func which it should run when the result comes back.

        return_in_future specifies
        '''
        log = self._get_log('_run_async')
        try:
            #log.debug('Run %s\n\twith args %s\n\tkwargs %s'\
            #                '\n\ttimeout %s\n\tstore result in future %s'\
            #                '\n\tand using callback %s (named %s)',
            #                async_func, args, kwargs, timeout, future,
            #                cb_func, callback_name)
            if args is None:
                args = ()
            if kwargs is None:
                kwargs = {}

            timeout_ref         = None
            return_result       = future is None

            if self._is_own_thread:
                #log.debug('We are running in our own thread')

                # We're in our own thread.  Is there a callback involved?
                if cb_func is None:
                    # There isn't.  This is easy then, just call the function and
                    # return the result.  Since the function is synchronous, we
                    # ignore the timeout.
                    if return_result:
                        #log.debug('Running directly')
                        result = async_func(*args, **kwargs)
                        raise tornado.gen.Return(result)
                    else:
                        try:
                            result = async_func(*args, **kwargs)
                            future.set_result(result)
                        except Exception,e:
                            log.exception('Exception running %s',
                                    async_func)
                            future.set_exception(e)
                else:
                    #log.debug('Running via callback')
                    # The result (or an exception) will be placed in this future.
                    future = future or tornado.concurrent.Future()
                    # Create a timeout object if we're given a time limit.
                    if timeout is not None:
                        timeout_ref = self._schedule_timeout(timeout, future)

                    # The function takes a callback argument which provides the
                    # result we're after.  We've been given the function that will
                    # rat through what was given to us and will provide the result.

                    # The first argument given to the callback is the future.
                    cb_func = self._get_callback(cb_func)
                    def _callback(*args, **kwargs):
                        log = self._get_log('_run_async._callback')
                        #log.debug('Got response args=%s, kwargs=%s',
                        #        args, kwargs)
                        try:
                            cb_func(future, *args, **kwargs)
                        except TimeoutError:
                            timeout_ref = None
                        except Exception, e:
                            if not future.done():
                                future.set_exception(e)
                            else:
                                log.exception('Exception in callback')
                    kwargs = kwargs.copy()
                    kwargs[callback_name] = _callback

                    # Perform the action given...
                    #log.debug('Performing asynchronous operation')
                    try:
                        #log.debug('Executing %s(*%s, **%s)',
                        #        async_func, args, kwargs)
                        async_func(*args, **kwargs)
                    except Exception, e:
                        if not return_result:
                            future.set_exception(e)
                        else:
                            raise
                    if timeout_ref is not None:
                        self._io_loop.remove_timeout(timeout_ref)
            else:
                assert self._io_thread.is_alive(), 'IO Thread is dead'
                #log.debug('Scheduling to run in our own IOLoop (we are '\
                #                'in a foreign thread; current=%s vs ours=%s)',
                #                threading.current_thread(), self._io_thread)
                # We're in the wrong thread, so schedule this to take place in
                # our own IOLoop.  First, create a future to store this in.
                future = future or tornado.concurrent.Future()
                # Then call ourselves with the new future.
                self._io_loop.add_callback(
                        self._run_async,
                        async_func=async_func,
                        args=args,
                        kwargs=kwargs,
                        timeout=timeout,
                        cb_func=cb_func,
                        callback_name=callback_name,
                        future=future)

            #log.debug('Return result? %s', return_result)
            if return_result:
                # Wait for the result
                #log.debug('Waiting for result')
                result = yield future
                if timeout_ref is not None:
                    self._io_loop.remove_timeout(timeout_ref)
                #log.debug('Result = %s', result)
                # Return the result
                raise tornado.gen.Return(result)
            else:
                # Return nothing to prevent the IOLoop from waiting.
                raise tornado.gen.Return(None)
        except tornado.gen.Return:
            raise
        except:
            log.exception('Failed to execute')
            raise

    def _get_callback(self, callback_ref, callback_args=None,
            callback_kwargs=None):
        '''
        Return a callback function from the given reference.
        '''
        #log = self._get_log('_get_callback')
        if callback_ref is None:
            return None

        if callback_args is None:
            callback_args = ()
        if callback_kwargs is None:
            callback_kwargs = {}

        if isinstance(callback_ref, tuple):
            (callback_ioloop, callback_func) = callback_ref[0:2]
            if len(callback_ref) > 2:
                callback_args = callback_args + (callback_ref[2] or ())
            if len(callback_ref) > 3:
                callback_kwargs.update(callback_ref[3] or {})
        else:
            callback_ioloop = None
            callback_func   = callback_ref

        if callback_ioloop is None:
            callback_ioloop = self._io_loop

        def _callback(*args, **kwargs):
            log = self._get_log('_get_callback','_callback')
            #log.debug('Called with\n\targs=%s,\n\tkwargs=%s', args, kwargs)

            # TODO: why is this happening?
            if (len(args) == 1) and isinstance(args[0], tuple):
                args = args[0]

            try:
                cb_args     = callback_args + args
                cb_kwargs   = callback_kwargs.copy()
                cb_kwargs.update(kwargs)
                if self._io_loop is callback_ioloop:
                    # We're running this ourselves
                    #log.debug('Calling function in own IOLoop')
                    cb_res  = callback_func(*args, **kwargs)
                    if isinstance(cb_res, tornado.concurrent.Future):
                        #log.debug(  'Function is asynchronous, '\
                        #            'waiting for result')
                        @tornado.gen.coroutine
                        def _get_result(future):
                            #log.debug('Getting result')
                            try:
                                result = yield future
                                #log.debug('Callback result: %s', result)
                            except:
                                log.exception('Callback failed')
                        self._io_loop.add_future(cb_res, _get_result)
                    #else:
                        #log.debug('Callback result: %s', cb_res)
                else:
                    #log.debug('Scheduling function in external IOLoop')
                    callback_ioloop.add_callback(
                            callback_func, *cb_args, **cb_kwargs)
                    #log.debug('Callback scheduled')
            except:
                log.exception('Callback failed: %s', callback_func)
        #log.debug('Wrapping function %s in callback %s',
        #        callback_func, _callback)
        return _callback

class AMQPChannel(AMQPObject):
    '''
    An abstraction for the AMQP Channel.
    '''

    def __init__(self, connection, channel_number):
        '''
        Initialise a new channel object.
        '''
        log = self._get_log('__init__')
        log.debug('New channel')
        self._connection    = connection
        self._channel_number= channel_number
        self._channel       = None

        # Queues and exchanges to re-establish
        self._exchanges     = []
        self._queues        = []

    _amqp_connection        = property(lambda s : \
            s._connection._amqp_connection)

    def _mark_stale(self):
        self._get_log('_mark_stale').debug(
                'Channel is now stale')
        self._channel       = None

    @tornado.gen.coroutine
    def _init_channel(self, timeout=None):
        log = self._get_log('channel')
        def _callback(future, channel):
            log.debug('Opened new channel %s', channel)
            if not future.done():
                future.set_result(channel)
            else:
                log.error('Future already done, cannot return channel')
                channel.close()
        log.debug('Opening new channel (number=%s)', self._channel_number)
        try:
            channel     = yield self._connection._run_async(
                    async_func      = self._amqp_connection.channel,
                    args            = None,
                    kwargs          = {'channel_number': self._channel_number},
                    timeout         = timeout,
                    cb_func         = _callback,
                    callback_name   = 'on_open_callback',
                    future          = None)
        except:
            log.exception('Failed to open channel')
            raise
        
        self._channel = channel

        # If we had any exchanges, declare those now
        for ex in self._get_exchanges():
            try:
                log.debug('Declaring exchange %s', ex.exchange)
                yield ex.declare(timeout)
            except:
                log.exception('Failed to declare exchange %s', ex.exchange)

        # If we had any queues, declare those now
        for q in self._get_queues():
            try:
                log.debug('Declaring queue %s', q.routing_key)
                yield q.declare(timeout)
            except:
                log.exception('Failed to declare exchange %s', q.routing_key)

    # ------------------------------------------------------------------------
    # Channel status
    # ------------------------------------------------------------------------

    is_closed   = property(lambda s : s._channel.is_closed)
    is_closing  = property(lambda s : s._channel.is_closing)
    is_open     = property(lambda s : s._channel.is_open)

    # ------------------------------------------------------------------------
    # Channel callbacks
    # ------------------------------------------------------------------------

    def add_callback(self, callback, replies, one_shot=True):
        return self._connection._run_async(
                async_func=self._channel.add_callback,
                args=(self._connection._get_callback(callback),
                    replies, one_shot),
                kwargs={}, timeout=None, callback=None, future=None)

    def add_on_cancel_callback(self, callback):
        return self._connection._run_async(
                self._channel.add_on_cancel_callback,
                    args=(self._connection._get_callback(callback),))

    def add_on_close_callback(self, callback):
        return self._connection._run_async(
                self._channel.add_on_close_callback,
                    args=(self._connection._get_callback(callback),))

    def add_on_flow_callback(self, callback):
        return self._connection._run_async(
                self._channel.add_on_flow_callback,
                    args=(self._connection._get_callback(callback),))

    def add_on_return_callback(self, callback):
        return self._connection._run_async(
                self._channel.add_on_return_callback,
                    args=(self._connection._get_callback(callback),))

    # ------------------------------------------------------------------------
    # Channel operations
    # ------------------------------------------------------------------------

    def basic_ack(self, delivery_tag=0, multiple=False):
        return self._connection._run_async(
                self._channel.basic_ack, args=(delivery_tag, multiple))

    def basic_cancel(self, callback=None, consumer_tag='', nowait=False):
        return self._connection._run_async(
                self._channel.basic_cancel,
                    args=(self._connection._get_callback(callback),
                    consumer_tag, nowait))

    def basic_consume(self, consumer_callback, queue='', no_ack=False,
            exclusive=False, consumer_tag=None, arguments=None):
        return self._connection._run_async(
            self._channel.basic_consume,
                args=(self._connection._get_callback(consumer_callback),
                queue, no_ack, exclusive, consumer_tag, arguments))

    def basic_get(self, callback, queue='', no_ack=False):
        return self._connection._run_async(
                self._channel.basic_get,
                    args=(self._connection._get_callback(callback),
                    queue, no_ack))

    def basic_nack(self, delivery_tag=None, multiple=False, requeue=True):
        return self._connection._run_async(
            self._channel.basic_nack,
                args=(delivery_tag, multiple, requeue))

    def basic_publish(self, exchange, routing_key, body, properties=None,
            mandatory=False, immediate=False):
        return self._connection._run_async(
            self._channel.basic_publish,
                args=(exchange, routing_key, body, properties,
                    mandatory, immediate))

    def basic_qos(self, callback=None, prefetch_size=0, prefetch_count=0,
            all_channels=False):
        return self._connection._run_async(
            self._channel.basic_qos,
                args=(self._connection._get_callback(callback),
                prefetch_size, prefetch_count, all_channels))

    def basic_reject(self, delivery_tag=None, requeue=True):
        return self._connection._run_async(
            self._channel.basic_reject,
                args=(delivery_tag, requeue))

    def basic_recover(self, callback=None, prefetch_size=0, prefetch_count=0,
            all_channels=False):
        return self._connection._run_async(
            self._channel.basic_qos,
                args=(self._connection._get_callback(callback),
                prefetch_size, prefetch_count, all_channels))

    def close(self, *args, **kwargs):
        return self._connection._run_async(
            self._channel.close,
                args=args, kwargs=kwargs)

    def confirm_delivery(self, callback=None, nowait=False):
        return self._connection._run_async(
            self._channel.confirm_delivery,
                args=(self._connection._get_callback(callback), nowait))

    def open(self):
        return self._connection._run_async(self._channel.open)

    # ------------------------------------------------------------------------
    # Exchange operations
    # ------------------------------------------------------------------------

    def _cleanup_exchanges(self):
        self._exchanges = filter(lambda er : er() is not None, self._exchanges)
    def _get_exchanges(self):
        return [er() for er in self._exchanges]

    @tornado.gen.coroutine
    def exchange(self, exchange=None, exchange_type='direct',
            passive=False, durable=False, auto_delete=False, internal=False,
            nowait=False, arguments=None, timeout=None):

        e   = AMQPExchange(self, exchange, exchange_type, passive, durable,
                auto_delete, internal, nowait, arguments)

        yield e.declare(timeout)
        self._cleanup_exchanges()
        self._exchanges.append(weakref.ref(e))
        raise tornado.gen.Return(e)

    def exchange_bind(self, destination=None, source=None,
                      routing_key='', nowait=False, arguments=None,
                      timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.exchange_bind,
                args=(destination, source, routing_key, nowait, arguments),
                cb_func=_get_response,
                timeout=timeout)

    def exchange_declare(self, exchange=None, exchange_type='direct',
            passive=False, durable=False, auto_delete=False, internal=False,
            nowait=False, arguments=None, timeout=None):

        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.exchange_declare,
                kwargs={
                    'exchange':         exchange,
                    'exchange_type':    exchange_type,
                    'passive':          passive,
                    'durable':          durable,
                    'auto_delete':      auto_delete,
                    'internal':         internal,
                    'nowait':           nowait,
                    'arguments':        arguments,
                },
                cb_func=_get_response,
                timeout=timeout)

    def exchange_delete(self, exchange=None, if_unused=False, nowait=False,
            timeout=None):

        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.exchange_delete,
                kwargs={
                    'exchange':     exchange,
                    'if_unused':    if_unused,
                    'nowait':       nowait,
                },
                cb_func=_get_response,
                timeout=timeout)

    def exchange_unbind(self, destination=None, source=None,
                        routing_key='', nowait=False, arguments=None,
                        timeout=None):

        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.exchange_unbind,
                kwargs={
                    'destination':  destination,
                    'source':       source,
                    'routing_key':  routing_key,
                    'nowait':       nowait,
                    'arguments':    arguments
                },
                cb_func=_get_response,
                timeout=timeout)

    # ------------------------------------------------------------------------
    # Flow operations
    # ------------------------------------------------------------------------

    def flow(self, callback, active):
        return self._connection._run_async(
            self._channel.flow,
                args=(self._connection._get_callback(callback), active))

    # ------------------------------------------------------------------------
    # Queue operations
    # ------------------------------------------------------------------------

    def _cleanup_queues(self):
        self._queues    = filter(lambda qr : qr() is not None, self._queues)
    def _get_queues(self):
        return [qr() for qr in self._queues]

    @tornado.gen.coroutine
    def queue(self, queue=None, passive=False, durable=False,
                exclusive=False, auto_delete=False, nowait=False,
                arguments=None, timeout=None):
        q   = AMQPQueue(self, queue, passive, durable, exclusive, auto_delete,
                nowait, arguments)
        yield q.declare(timeout)
        self._cleanup_queues()
        self._queues.append(weakref.ref(q))
        raise tornado.gen.Return(q)

    def queue_bind(self, queue, exchange, routing_key=None,
                   nowait=False, arguments=None, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.queue_bind,
                kwargs={
                    'queue':        queue,
                    'exchange':     exchange,
                    'routing_key':  routing_key,
                    'nowait':       nowait,
                    'arguments':    arguments,
                },
                cb_func=_get_response,
                timeout=timeout)

    def queue_declare(self, queue='', passive=False, durable=False,
                      exclusive=False, auto_delete=False, nowait=False,
                      arguments=None, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.queue_declare,
                kwargs={
                    'queue':        queue,
                    'passive':      passive,
                    'durable':      durable,
                    'exclusive':    exclusive,
                    'auto_delete':  auto_delete,
                    'nowait':       nowait,
                    'arguments':    arguments,
                },
                cb_func=_get_response,
                timeout=timeout)

    def queue_delete(self, queue='', if_unused=False,
                     if_empty=False, nowait=False, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.queue_delete,
                kwargs={
                    'queue':        queue,
                    'if_unused':    if_unused,
                    'if_empty':     if_empty,
                    'nowait':       nowait
                },
                cb_func=_get_response,
                timeout=timeout)

    def queue_purge(self, queue, nowait=False, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.queue_purge,
                kwargs={
                    'queue':        queue,
                    'nowait':       nowait
                },
                cb_func=_get_response,
                timeout=timeout)

    def queue_unbind(self, queue='', exchange=None,
                     routing_key=None, arguments=None, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.queue_unbind,
                kwargs={
                    'queue':        queue,
                    'exchange':     exchange,
                    'routing_key':  routing_key,
                    'arguments':    arguments
                },
                cb_func=_get_response,
                timeout=timeout)

    # ------------------------------------------------------------------------
    # Transaction operations
    # ------------------------------------------------------------------------

    def tx_commit(self, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.tx_commit,
                cb_func=_get_response,
                timeout=timeout)

    def tx_rollback(self, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.tx_rollback,
                cb_func=_get_response,
                timeout=timeout)

    def tx_select(self, timeout=None):
        def _get_response(future, response):
            future.set_result(response)
        return self._connection._run_async(
                self._channel.tx_select,
                cb_func=_get_response,
                timeout=timeout)

class AMQPMessageDestination(AMQPObject):
    '''
    A AMQPMessageDestination object is a base class for Queues and Exchanges:
    places you can send messages to.  This base class handles the transmission
    of a message.
    '''

    def __init__(self, channel, exchange, routing_key):
        self._channel       = channel
        self._exchange      = exchange
        self._routing_key   = routing_key
        self._declared      = False

    _connection             = property(lambda s : s._channel._connection)
    _amqp_connection        = property(lambda s : s._channel._amqp_connection)

    exchange    = property(lambda s : s._exchange)
    routing_key = property(lambda s : s._routing_key)

    @tornado.gen.coroutine
    def basic_publish(self, body, properties=None, mandatory=False,
            immediate=False, exchange=None, routing_key=None):

        if exchange is None:
            exchange    = self.exchange
        if routing_key is None:
            routing_key = self.routing_key

        raise tornado.gen.Return((
            yield self._channel.basic_publish(
                exchange, routing_key, body, properties, mandatory,
                immediate)
        ))

class AMQPQueue(AMQPMessageDestination):
    '''
    A representation of a message queue.
    '''
    def __init__(self, channel, queue=None, passive=False, durable=False,
            exclusive=False, auto_delete=False, nowait=False, arguments=None):

        super(AMQPQueue, self).__init__(channel, '', None)
        self._queue         = queue
        self._passive       = passive
        self._durable       = durable
        self._exclusive     = exclusive
        self._auto_delete   = auto_delete
        self._nowait        = nowait
        self._arguments     = arguments

        # Our bindings to instate
        # Format:
        # {
        #   exchange_name: {
        #       routing_key:    {
        #           args:           kwargs for queue_bind,
        #           bound:          boolean indicating bind state,
        #       }
        #   },
        # }
        self._bindings      = {}

        # A list of consumers
        self._consumers     = []

    # ------------------------------------------------------------------------
    # Queue operations
    # ------------------------------------------------------------------------

    @tornado.gen.coroutine
    def declare(self, timeout=None):
        log = self._get_log('declare')
        # Are we declaring passively?
        if self._passive:
            # We are, declare using a temporary channel
            log.debug('Using temporary channel')
            ch  = yield self._channel._connection.channel()
        else:
            # We're not, use our own channel
            log.debug('Using own channel')
            ch  = self._channel

        # Declare the queue in the channel
        try:
            log.debug('Declaring queue')
            queue_res = yield ch.queue_declare(
                    queue       = self._queue or '',
                    passive     = self._passive,
                    durable     = self._durable,
                    exclusive   = self._exclusive,
                    auto_delete = self._auto_delete,
                    nowait      = self._nowait,
                    arguments   = self._arguments,
                    timeout     = timeout)
            self._routing_key   = queue_res.method.queue
            log.debug('Queue is %s', self._routing_key)
        except:
            log.exception('Failed to declare queue (queue=%s)', self._queue)

        # If we opened a temporary channel, close it
        if self._passive and ch.is_open:
            yield ch.close()

        # If we were bound to things, re-bind
        for exchange, bindings in self._bindings.copy().iteritems():
            for routing_key, state in bindings.copy().iteritems():
                yield self.bind(
                        exchange    = exchange,
                        routing_key = routing_key,
                        nowait      = state['args']['nowait'],
                        arguments   = state['args']['arguments'],
                        timeout     = timeout)

        # If we have any consumers, re-start those
        for c in self._get_consumers():
            yield c.consume(timeout)

    @tornado.gen.coroutine
    def bind(self, exchange, routing_key=None,
            nowait=False, arguments=None, timeout=None):
        log = self._get_log('bind')

        if isinstance(exchange, AMQPExchange):
            exchange    = exchange.exchange

        state = {
                'args': {
                    'nowait':       nowait,
                    'arguments':    arguments,
                },
                'bound':            False,
        }
        try:
            log.debug('Binding to %s:%s', exchange, routing_key)

            result = yield self._channel.queue_bind(
                    queue       = self.routing_key,
                    exchange    = exchange or '',
                    routing_key = routing_key,
                    nowait      = nowait,
                    arguments   = arguments,
                    timeout     = timeout)
            # We should be bound now.
            state['bound'] = True
        except:
            log.debug('Failed to bind to %s:%s', exchange, routing_key)

        if exchange not in self._bindings:
            self._bindings[exchange] = {}
        self._bindings[exchange][routing_key] = state
        raise tornado.gen.Return(state['bound'])
    
    @tornado.gen.coroutine
    def delete(self, if_unused=False, if_empty=False, nowait=False,
            timeout=None):
        log = self._get_log('delete')
        try:
            log.debug('Deleting queue %s', self.routing_key)
            yield self._channel.queue_delete(
                    queue       = self.routing_key,
                    if_unused   = if_unused,
                    if_empty    = if_empty,
                    nowait      = nowait,
                    timeout     = timeout
            )
            # We're deleted
            self._routing_key   = None
        except:
            log.exception('Failed to delete queue %s', self.routing_key)
            raise

    @tornado.gen.coroutine
    def purge(self, queue, nowait=False, timeout=None):
        yield self._channel.queue_purge(
                queue           = self.routing_key,
                nowait          = nowait,
                timeout         = timeout)

    @tornado.gen.coroutine
    def unbind(self, exchange=None, routing_key=None,
            arguments=None, timeout=None):

        if isinstance(exchange, AMQPExchange):
            exchange    = exchange.exchange

        yield self._channel.queue_unbind(
                queue       = self.routing_key,
                exchange    = exchange,
                routing_key = routing_key,
                arguments   = arguments,
                timeout     = timeout)
        # If we got here, then we're unbound
        try:
            del(self._bindings[exchange][routing_key])
            if len(self._bindings[exchange]) == 0:
                del(self._bindings[exchange])
        except KeyError:
            pass

    def _cleanup_consumers(self):
        self._consumers = filter(lambda cr : cr() is not None, self._consumers)
    def _get_consumers(self):
        return [cr() for cr in self._consumers]

    @tornado.gen.coroutine
    def consume(self, consumer_callback, no_ack=False, exclusive=False,
            consumer_tag=None, arguments=None, channel=None, timeout=None):

        c   = AMQPConsumer(channel or self._channel, consumer_callback, self,
                no_ack, exclusive, consumer_tag, arguments)

        yield c.consume(timeout)
        self._cleanup_consumers()
        self._consumers.append(weakref.ref(c))
        raise tornado.gen.Return(c)

class AMQPExchange(AMQPMessageDestination):
    '''
    A representation of a message exchange.
    '''
    def __init__(self, channel, exchange=None, exchange_type='direct',
            passive=False, durable=False, auto_delete=False, internal=False,
            nowait=False, arguments=None):

        super(AMQPExchange, self).__init__(channel, exchange, None)
        self._exchange_type = exchange_type
        self._passive       = passive
        self._durable       = durable
        self._auto_delete   = auto_delete
        self._internal      = internal
        self._nowait        = nowait
        self._arguments     = arguments
        self._declared      = False

        # Our bindings to instate
        # Format:
        # {
        #   exchange_name: {
        #       routing_key:    {
        #           args:           kwargs for queue_bind,
        #           bound:          boolean indicating bind state,
        #       }
        #   },
        # }
        self._bindings      = {}

    # ------------------------------------------------------------------------
    # Exchange operations
    # ------------------------------------------------------------------------

    @tornado.gen.coroutine
    def declare(self, timeout=None):
        log = self._get_log('declare')
        # Are we declaring passively?
        if self._passive:
            # We are, declare using a temporary channel
            log.debug('Using temporary channel')
            ch  = yield self._channel._connection.channel()
        else:
            # We're not, use our own channel
            log.debug('Using own channel')
            ch  = self._channel

        # Declare the queue in the channel
        try:
            log.debug('Declaring exchange')
            queue_res = yield ch.exchange_declare(
                    exchange        = self._exchange,
                    exchange_type   = self._exchange_type,
                    passive         = self._passive,
                    durable         = self._durable,
                    auto_delete     = self._auto_delete,
                    internal        = self._internal,
                    nowait          = self._nowait,
                    arguments       = self._arguments,
                    timeout         = timeout)
            self._declared          = True
            log.debug('Exchange declared')
        except:
            log.exception('Failed to declare exchange %s', self._exchange)

        # If we opened a temporary channel, close it
        if self._passive and ch.is_open:
            yield ch.close()

        # If we were bound to things, re-bind
        for exchange, bindings in self._bindings.copy().iteritems():
            for routing_key, state in bindings.copy().iteritems():
                yield self.bind(
                        exchange    = exchange,
                        routing_key = routing_key,
                        nowait      = state['args']['nowait'],
                        arguments   = state['args']['arguments'],
                        timeout     = timeout)


    @tornado.gen.coroutine
    def bind(self, exchange, routing_key=None,
            nowait=False, arguments=None, timeout=None):
        log = self._get_log('bind')

        if isinstance(exchange, AMQPExchange):
            exchange    = exchange.exchange

        state = {
                'args': {
                    'nowait':       nowait,
                    'arguments':    arguments,
                },
                'bound':            False,
        }
        try:
            log.debug('Binding to %s:%s', exchange, routing_key)

            result = yield self._channel.queue_bind(
                    destination = self.exchange,
                    source      = exchange,
                    routing_key = routing_key or '',
                    nowait      = nowait,
                    arguments   = arguments,
                    timeout     = timeout)
            # We should be bound now.
            state['bound'] = True
        except:
            log.debug('Failed to bind to %s:%s', exchange, routing_key)

        if exchange not in self._bindings:
            self._bindings[exchange] = {}
        self._bindings[exchange][routing_key] = state
        raise tornado.gen.Return(state['bound'])
    
    @tornado.gen.coroutine
    def delete(self, if_unused=False, nowait=False, timeout=None):
        log = self._get_log('delete')
        try:
            log.debug('Deleting exchange %s', self.exchange)
            yield self._channel.exchange_delete(
                    exchange    = self.exchange,
                    if_unused   = if_unused,
                    nowait      = nowait,
                    timeout     = timeout
            )
            self._declared      = False
        except:
            log.exception('Failed to delete exchange %s', self.exchange)
            raise

    @tornado.gen.coroutine
    def unbind(self, exchange=None, routing_key=None,
            arguments=None, timeout=None):

        if isinstance(exchange, AMQPExchange):
            exchange    = exchange.exchange

        yield self._channel.exchange_unbind(
                destination = self.exchange,
                source      = exchange,
                routing_key = routing_key,
                arguments   = arguments,
                timeout     = timeout)
        # If we got here, then we're unbound
        try:
            del(self._bindings[exchange][routing_key])
            if len(self._bindings[exchange]) == 0:
                del(self._bindings[exchange])
        except KeyError:
            pass

class AMQPConsumer(AMQPObject):
    '''
    An abstraction for a consumer.
    '''

    def __init__(self, channel, consumer_callback, queue=None, no_ack=False,
            exclusive=False, consumer_tag=None, arguments=None):

        self._channel           = channel
        self._consumer_callback = consumer_callback
        self._queue             = queue
        self._no_ack            = no_ack
        self._exclusive         = exclusive
        self._consumer_tag_given= consumer_tag
        self._arguments         = arguments
        self._consumer_tag      = None

    consumer_tag                = property(lambda s : s._consumer_tag)

    @tornado.gen.coroutine
    def consume(self, timeout=None):
        log = self._get_log('_consume')
        try:
            log.debug('Consuming queue %s', self._queue.routing_key)
            result = yield self._channel.basic_consume(
                    consumer_callback   = self._consumer_callback,
                    queue               = self._queue.routing_key,
                    no_ack              = self._no_ack,
                    exclusive           = self._exclusive,
                    consumer_tag        = self._consumer_tag_given,
                    arguments           = self._arguments)
            self._consumer_tag          = result
            log.debug('Consumer tag is %s', self._consumer_tag)
        except:
            log.exception('Failed to consume %s', self._queue.routing_key)
            self._consumer_tag          = None
            raise

    @tornado.gen.coroutine
    def cancel(self, nowait=False, arguments=None, timeout=None):
        log = self._get_log('cancel')
        try:
            log.debug('Cancelling consumer of queue %s', self._queue.routing_key)
            yield self._channel.basic_cancel(
                    consumer_tag        = self._consumer_tag_given,
                    nowait              = nowait,
                    arguments           = arguments)
            self._consumer_tag          = None
            log.debug('Consumer is cancelled')
        except:
            log.exception('Failed to cancel consuming %s',
                    self._queue.routing_key)
            raise

class TimeoutError(Exception):
    '''
    Exception raised when an operation times out.
    '''
    pass

if __name__ == '__main__':
    # The following is a simple example that tries to
    # create two channels (transmit and receive), declare an exchange,
    # bind a new queue to it, then send a message to the exchange.
    logging.basicConfig(
            level=logging.DEBUG,
            format= '%(asctime)s %(name)s[%(filename)s:%(lineno)4d] '\
                    '%(process)d/%(threadName)s %(levelname)s %(message)s')
    io_loop = tornado.ioloop.IOLoop.instance()
    msg_received = tornado.concurrent.Future()

    @tornado.gen.coroutine
    def receive(channel, method, properties, body):
        logging.info(
                ('\n' + ('-'*80) +
                '\nReceived\n\tchannel=%s,\n\tmethod=%s,'\
                '\n\tproperties=%s, body=%s\n' +
                ('-'*80)),
                channel, method, properties, body)
        msg_received.set_result(True)
        raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def on_connect(*args, **kwargs):
        try:
            logging.info('Opening a transmit channel')
            tx_ch = yield amqp_conn.channel()
            logging.debug('tx_ch = %s', tx_ch)
            logging.info('Opening a receive channel')
            rx_ch = yield amqp_conn.channel()
            logging.info('Declaring a test exchange on the receive channel')
            ex = yield rx_ch.exchange_declare(exchange='test',
                    exchange_type='fanout')
            logging.info('Declaring a receive queue on the receive channel')
            rx_q  = yield rx_ch.queue_declare(exclusive=True)
            logging.info('Binding the queue to the exchange')
            bind  = yield rx_ch.queue_bind( queue=rx_q.method.queue,
                                            exchange='test', routing_key='#')
            logging.info('Beginning consumation of queue')
            consume = yield rx_ch.basic_consume(
                    consumer_callback = receive,
                    queue = rx_q.method.queue,
                    no_ack=True)
            logging.info('Transmitting a test message')
            tx = yield tx_ch.basic_publish(
                    exchange = 'test',
                    routing_key = 'test',
                    body = 'this is a test')
            logging.info('Waiting to receive something')
            yield msg_received
            logging.info('Disconnecting')
            yield amqp_conn.close()
            logging.info('Stopping')
        except:
            logging.exception('on_connect failed')
        io_loop.stop()
        raise tornado.gen.Return(None)

    amqp_conn = AMQPConnection(
            pika.URLParameters('amqp://guest:guest@localhost:5672/%2f'),
            io_loop=io_loop,
            on_open_callback=on_connect)
    io_loop.start()