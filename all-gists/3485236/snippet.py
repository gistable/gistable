class FrealCountdownTask(task.Task):
    abstract = True

    @classmethod
    def apply_async(self, args=None, kwargs=None,
            task_id=None, producer=None, connection=None, router=None,
            link=None, link_error=None, publisher=None, add_to_parent=True,
            **options):

        try:
            countdown = options.pop('countdown')
        except KeyError:
            # no countdown, call super as normal
            return super(FrealCountdownTask, self).apply_async(args=args,
                kwargs=kwargs, task_id=task_id, producer=producer,
                connection=connection, router=router, link=link,
                link_error=link_error, publisher=publisher,
                add_to_parent=add_to_parent, **options)

        # resolve full list of options (taken from Task.apply_async)
        app = self._get_app()
        router = router or self.app.amqp.router
        options = dict(extract_exec_options(self), **options)
        options = router.route(options, self.name, args, kwargs)


        # add the queue to the app so celery knows about it and use that queue
        # for this task
        task_id = task_id or gen_unique_id()
        app.amqp.queues.add(task_id, exchange=settings.COUNTDOWN_EXCHANGE.name,
            exchange_type=settings.COUNTDOWN_EXCHANGE.type,
            routing_key=options['routing_key'], queue_arguments={
                'x-message-ttl': countdown * 1000,
                'x-dead-letter-exchange': options['queue'],
                'x-expires': (countdown + 1) * 1000,
            })
        options.update({
            'queue': task_id,
            'exchange': settings.COUNTDOWN_EXCHANGE,
        })

        return super(FrealCountdownTask, self).apply_async(args=args,
            kwargs=kwargs, task_id=task_id, producer=producer,
            connection=connection, router=router, link=link,
            link_error=link_error, publisher=publisher,
            add_to_parent=add_to_parent, **options)
