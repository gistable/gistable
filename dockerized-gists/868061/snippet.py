from threading import local

_blah = local()

class StopThatShit(Exception):
    pass

def patch():
    from django.db.backends import util
    from django import template
    
    class StopQueryingCursorWrapper(util.CursorWrapper):
        def __init__(self, cursor, connection):
            if getattr(_blah, 'rendering', False):
                raise StopThatShit('Stop executing queries in your templates!')
            super(StopQueryingCursorWrapper, self).__init__(cursor, connection)
    util.CursorWrapper = StopQueryingCursorWrapper

    class StopQueryingTemplate(template.Template):
        def render(self, context):
            _blah.rendering = True
            try:
                super(StopQueryingTemplate, self).__init__(context)
            finally:
                _blah.rendering = False
    template.Template = StopQueryingTemplate