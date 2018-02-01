from collections import OrderedDict


class Event(object):
    def __init__(self):
        self.__name = None

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name


class EventSubscriberInterface(object):
    def getSubscribedEvents(self):
        raise NotImplementedError()


class EventDispatcher(object):
    def __init__(self):
        self._listeners = {}

    def dispatch(self, eventName, event=None):
        if event is None:
            event = Event()
        elif not isinstance(event, Event):
            raise ValueError('Unexpected event type given')
        event.setName(eventName)
        if eventName not in self._listeners:
            return event
        for listener in self._listeners[eventName].values():
            listener(event, self)
        return event

    def addListener(self, eventName, listener, priority=0):
        if eventName not in self._listeners:
            self._listeners[eventName] = {}
        self._listeners[eventName][priority] = listener
        self._listeners[eventName] = OrderedDict(sorted(self._listeners[eventName].items(), key=lambda item: item[0]))

    def removeListener(self, eventName, listener=None):
        if eventName not in self._listeners:
            return
        if not listener:
            del self._listeners[eventName]
        else:
            for p, l in self._listeners[eventName].items():
                if l is listener:
                    self._listeners[eventName].pop(p)
                    return

    def addSubscriber(self, subscriber):
        if not isinstance(subscriber, EventSubscriberInterface):
            raise ValueError('Unexpected subscriber type given')
        for eventName, params in subscriber.getSubscribedEvents().items():
            if isinstance(params, str):
                self.addListener(eventName, getattr(subscriber, params))
            elif isinstance(params, list):
                if not params:
                    raise ValueError('Invalid params "%r" for event "%s"' % (params, eventName))
                if len(params) <= 2 and isinstance(params[0], str):
                    priority = params[1] if len(params) > 1 else 0
                    self.addListener(eventName, getattr(subscriber, params[0]), priority)
                else:
                    for listener in params:
                        priority = listener[1] if len(listener) > 1 else 0
                        self.addListener(eventName, getattr(subscriber, listener[0]), priority)
            else:
                raise ValueError('Invalid params for event "%s"' % eventName)


# USAGE

def one(event, dispatcher):
    print(1, event.getName(), event.data)


class Subscriber(EventSubscriberInterface):
    def zero(self, event, dispatcher):
        print(0, event.getName(), event.data)
        dispatcher.dispatch('event2', CustomEvent())

    def two(self, event, dispatcher):
        print(2, event.getName(), event.data)

    def three(self, event, dispatcher):
        print(3, event.getName(), event.data)

    def four(self, event, dispatcher):
        print(4, event.getName(), event.data)

    def five(self, event, dispatcher):
        print(5, event.getName(), event.data)

    def getSubscribedEvents(self):
        return {
            'event': [
                ['zero'],
                ['two', 2],
                ['three', 3],
                ['four', 4],
                ['five', 5]
            ]
        }


class CustomEvent(Event):
    def __init__(self):
        self.data = 'Data'


def event2Listener(event, dispatcher):
    print(event.getName())


d = EventDispatcher()
d.addListener('event', one, 1)
d.addListener('event2', event2Listener)
d.addSubscriber(Subscriber())
d.dispatch('event', CustomEvent())

# Output:
# 0 event Data
# event2
# 1 event Data
# 2 event Data
# 3 event Data
# 4 event Data
# 5 event Data

d.removeListener('event', one)
d.removeListener('event2', event2Listener)
d.dispatch('event', CustomEvent())

# Output:
# (0, 'event', 'Data')
# (2, 'event', 'Data')
# (3, 'event', 'Data')
# (4, 'event', 'Data')
# (5, 'event', 'Data')

d.removeListener('event')
d.dispatch('event', CustomEvent())

# Output: Nothing
