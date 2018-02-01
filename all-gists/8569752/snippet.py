from threading import Thread
from time import sleep

from atom.api import Atom, Bool, Int

from enaml.application import deferred_call
from enaml.widgets.api import Window, Container, ProgressBar, PushButton


class Model(Atom):
    busy = Bool(False)
    value = Int(0)


def worker(model):
    p = 0
    while p <= 100:
        deferred_call(setattr, model, 'value', p)
        p += 1
        sleep(0.2)
    deferred_call(setattr, model, 'busy', False)


def do_it_if_needed(model):
    if not model.busy:
        model.busy = True
        thread = Thread(target=worker, args=(model,))
        thread.daemon = True
        thread.start()


enamldef Main(Window): main:
    title = 'Thread Ticker'
    attr model = Model()
    Container:
        ProgressBar:
            value << model.value
        PushButton:
            text = 'Do It!'
            clicked :: do_it_if_needed(model)
