from django.db.models.query import QuerySet
from django.db.models import Manager
from datetime import date


class EventQuerySet(QuerySet):
    def published(self):
        return self.filter(published=True)

    def available_for_adding(self):
        return self.filter(published=True, private=False)

    def active(self):
        return self.filter(event_time__start_date__gte=date.today())

    def date_filter(self, start_date, end_date):
        return self.filter(event_time__start_date__gte=start_date, event_time__end_date__lte=end_date)


class EventManager(Manager):
    def get_query_set(self):
        return EventQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_query_set().published()

    def available_for_adding(self):
        return self.get_query_set().available_for_adding()

    def active(self):
        return self.get_query_set().active()

    def date_filter(self, start_date, end_date):
        return self.get_query_set().date_filter(start_date, end_date)