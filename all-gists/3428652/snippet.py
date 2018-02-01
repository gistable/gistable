def shutdown(graceful=True):
    """Shut down the application.

    If a graceful stop is requested, waits for all of the IO loop's
    handlers to finish before shutting down the rest of the process.
    We impose a 10 second timeout.
    """
    ioloop = tornado.ioloop.IOLoop.instance()

    def final_stop():
        ioloop.stop()
        sys.exit(0)

    def poll_stop():
        remaining = len(ioloop._handlers)
        logging.info("[%d] Waiting on IO handlers (%d remaining)",
                tornado.process.task_id() or 0, remaining)
        # Wait until we only have only one IO handler remaining.  That
        # final handler will be our PeriodicCallback polling task.
        if remaining == 1:
            final_stop()

    if ioloop.running() and graceful:
        # Poll the IO loop's handlers until they all shut down.
        poller = tornado.ioloop.PeriodicCallback(poll_stop, 250,
                io_loop=ioloop)
        poller.start()

        # Give up after 10 seconds of waiting.
        ioloop.add_timeout(time.time() + 10, final_stop)
    else:
        final_stop()