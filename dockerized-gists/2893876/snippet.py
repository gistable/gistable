#!/usr/bin/env python
'''
Just a silly example for an Observer implementation using the "push event" method. See discussion about it:
https://groups.google.com/forum/?fromgroups#!topic/growing-object-oriented-software/KwJPxUZ0l_M
'''

class OrderTrackingEvent(object):
    def __init__(self, order_number, status):
        self.order_number = order_number
        self.status = status


class OrderTrackingBroadcaster(object):
    def __init__(self):
        self.listeners = []

    def broadcast(self, order_number, status):
        event = OrderTrackingEvent(order_number, status)
        self._notify(event)

    def add_listeners(self, *listeners):
        self.listeners.extend(listeners)

    def _notify(self, event):
        print '- starting broadcast -'
        for listener in self.listeners:
            listener.update(event)


class CouponListener(object):
    def update(self, event):
        if event.status == 'canceled':
            CouponService().cancel_for(order_number=event.order_number)


class CustomerListener(object):
    def update(self, event):
        CustomerService().send_for(order_number=event.order_number, status=event.status)


class CouponService(object):
    def cancel_for(self, order_number):
        print 'canceling coupons for order %d' % order_number


class CustomerService(object):
    def send_for(self, order_number, status):
        print 'sending notification e-mail for user from order %d about status "%s"' % (order_number, status)


if __name__ == '__main__':
    broadcaster = OrderTrackingBroadcaster()
    broadcaster.add_listeners(CouponListener(), CustomerListener())

    broadcaster.broadcast(1234, 'created')
    broadcaster.broadcast(5678, 'canceled')

