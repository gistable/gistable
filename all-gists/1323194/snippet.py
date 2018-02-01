# -*- coding: utf-8 -*-

from datetime import datetime
import sublime_plugin


class TimestampCommand(sublime_plugin.EventListener):
    """Expand `isoD`, `now`, `datetime`, `utcnow`, `utcdatetime`, 
       `date` and `time`
    """
    def on_query_completions(self, view, prefix, locations):
        if prefix in ('isoD', 'now', 'datetime'):
            val = datetime.now().strftime('%Y-%M-%dT%H:%M:%S')
        elif prefix in ('utcnow', 'utcdatetime'):
            val = datetime.utcnow().strftime('%Y-%M-%dT%H:%M:%S')
        elif prefix == 'date':
            val = datetime.now().strftime('%Y-%M-%d')
        elif prefix == 'time':
            val = datetime.now().strftime('%H:%M:%S')
        else:
            val = None

        return [(prefix, prefix, val)] if val else []
