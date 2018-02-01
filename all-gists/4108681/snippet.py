# Record handler exceptions for New Relic
def _new_internalerror(orig_internalerror):
    def inner():
        e = orig_internalerror()
        if isinstance(e, web.webapi._InternalError):
            e.orig_exc_info = sys.exc_info()
        return e
    return inner
def catch_and_report_exceptions(handler):
    try:
        return handler()
    except Exception, e:
        if hasattr(e, 'orig_exc_info'):
            newrelic.agent.record_exception(*e.orig_exc_info)
            e.orig_exc_info = None  # not today, leaks.
        raise
app.internalerror = _new_internalerror(app.internalerror)
app.add_processor(catch_and_report_exceptions)