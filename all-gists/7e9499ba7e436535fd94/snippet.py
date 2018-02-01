from django.db import transaction

class AtomicMixin(object):
    """
    Ensures we rollback db transactions on exceptions.
    Idea from https://github.com/tomchristie/django-rest-framework/pull/1204
    """
    @transaction.atomic()
    def dispatch(self, *args, **kwargs):
        return super(AtomicMixin, self).dispatch(*args, **kwargs)

    def handle_exception(self, *args, **kwargs):
        response = super(AtomicMixin, self).handle_exception(*args, **kwargs)

        if getattr(response, 'exception'):
            # We've suppressed the exception but still need to rollback any transaction.
            transaction.set_rollback(True)

        return response