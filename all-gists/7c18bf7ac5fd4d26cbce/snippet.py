from ansible import playbook, callbacks
import logging
import pprint


class LoggingCallbacks(callbacks.PlaybookCallbacks):
    def log(self, level, msg, *args, **kwargs):
        logging.log(level, msg, *args, **kwargs)

    def on_task_start(self, name, is_conditional):
        self.log(logging.INFO, 'task: {0}'.format(name))
        super(LoggingCallbacks, self).on_task_start(name, is_conditional)


class LoggingRunnerCallbacks(callbacks.PlaybookRunnerCallbacks):
    def log(self, level, msg, *args, **kwargs):
        logging.log(level, msg, *args, **kwargs)

    def _on_any(self, level, label, host, orig_result):
        result = orig_result.copy()
        result.pop('invocation', None)
        result.pop('verbose_always', True)
        item = result.pop('item', None)
        if not result:
            msg = ''
        elif len(result) == 1:
            msg = ' | {0}'.format(result.values().pop())
        else:
            msg = '\n' + pprint.pformat(result)
        if item:
            self.log(level, '{0} (item={1}): {2}{3}'.format(host, item, label, msg))
        else:
            self.log(level, '{0}: {1}{2}'.format(host, label, msg))

    def on_failed(self, host, res, ignore_errors=False):
        if ignore_errors:
            level = logging.INFO
            label = 'FAILED (ignored)'
        else:
            level = logging.ERROR
            label = 'FAILED'
        self._on_any(level, label, host, res)
        super(LoggingRunnerCallbacks, self).on_failed(host, res, ignore_errors)

    def on_ok(self, host, res):
        self._on_any(logging.INFO, 'SUCCESS', host, res)
        super(LoggingRunnerCallbacks, self).on_ok(host, res)

    def on_error(self, host, msg):
        self.log(logging.ERROR, '{0}: ERROR | {1}'.format(host, msg))
        super(LoggingRunnerCallbacks, self).on_error(host, msg)

    def on_skipped(self, host, item=None):
        if item:
            self.log(logging.INFO, '{0} (item={1}): SKIPPED'.format(host, item))
        else:
            self.log(logging.INFO, '{0}: SKIPPED'.format(host))
        super(LoggingRunnerCallbacks, self).on_skipped(host, item)

    def on_unreachable(self, host, res):
        self._on_any(logging.ERROR, 'UNREACHABLE', host, dict(unreachable=res))
        super(LoggingRunnerCallbacks, self).on_unreachable(host, res)

    def on_no_hosts(self):
        self.log(logging.ERROR, 'No hosts matched')
        super(LoggingRunnerCallbacks, self).on_no_hosts()


def run_playbook(path, extra_vars):
    stats = callbacks.AggregateStats()
    playbook_cb = LoggingCallbacks(verbose=3)
    runner_cb = LoggingRunnerCallbacks(stats, verbose=3)

    pb = playbook.PlayBook(
        playbook=path,
        stats=stats,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        extra_vars=extra_vars)
    pb.run()
    if stats.failures or stats.dark:
        raise RuntimeError('Playbook {0} failed'.format(path))
    return pb.SETUP_CACHE['localhost']
