class MyHTTPServer(tornado.httpserver.HTTPServer):
    _stopped = False

    def _quit_if_ioloop_is_empty(self):
        ioloop = tornado.ioloop.IOLoop.instance()
        if len(ioloop._handlers) <= 1:
            logger.info("Graceful shutdown complete. Exiting!")
            exit(0)
        else:
            logger.info("Waiting for ioloop to be empty. has %d handlers left" % len(ioloop._handlers))
    def _setup_worker_handlers(self):
        def quick_shutdown_handler(signum, frame):
            logger.warning("worker received signal %d. exiting immediately" % signum)
            exit(0)

        def graceful_shutdown_handler(signum, frame):
            logger.warning("worker received signal %d. gracefully shutting down" % signum)
            if not self._stopped:
                self.no_keep_alive = True
                self._stopped = True
                self.stop()
                
                max_wait_seconds = 100
                logger.info("Waiting for all connections to finish or %d seconds to pass (setting SIGALRM)" % max_wait_seconds)
                signal.signal(signal.SIGALRM, quick_shutdown_handler)
                signal.alarm(max_wait_seconds)

                pc = tornado.ioloop.PeriodicCallback(self._quit_if_ioloop_is_empty, 100, io_loop=tornado.ioloop.IOLoop.instance())
                pc.start()
                
            else:
                logger.warning("worker received signal %d. graceful shutdown has already begun" % signum)

        signal.signal(signal.SIGINT, quick_shutdown_handler)
        signal.signal(signal.SIGTERM, quick_shutdown_handler)
        signal.signal(signal.SIGQUIT, graceful_shutdown_handler)

    def _setup_main_handlers(self):
        def quick_shutdown_handler(signum, frame):
            logger.warning("main received signal %d. Shutting down worker quickly" % signum)
            if self.child_pid:
                os.kill(self.child_pid, signum)
                os.waitpid(self.child_pid, 0)
            logger.warning("Child shut down successfully")

        def graceful_shutdown_handler(signum, frame):
            logger.warning("main received signal %d. Shutting down worker gracefully" % signum)
            if self.child_pid:
                os.kill(self.child_pid, signum)
                logger.warning("main process exiting and detatching child")
            exit(0)

        signal.signal(signal.SIGINT, quick_shutdown_handler)
        signal.signal(signal.SIGTERM, quick_shutdown_handler)
        signal.signal(signal.SIGQUIT, graceful_shutdown_handler)

    def start(self, num_processes=1):
        if num_processes != 1:
            logger.error("We can only support one process. Setting to 1")
            num_processes = 1

        self.child_pid = os.fork()
        if not self.child_pid:
            self._setup_worker_handlers()
            tornado.httpserver.HTTPServer.start(self, num_processes)
        else:
            self._setup_main_handlers()
            logger.info("Waiting on child pid %d" % self.child_pid)
            try: 
                os.waitpid(self.child_pid, 0)
                logger.info("Child process appears to have exited")
                self.child_pid = None
            except OSError, e:
                if e.errno != 4:
                    raise
            finally:
                exit(0)
