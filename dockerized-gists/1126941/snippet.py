#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Monkey Patch for tornado
"""
import cProfile as profile

from tornado.options import options
from tornado.web import HTTPError

def profile_patch(execute):
    def _(self, transforms, *args, **kwargs):
        if options.is_debug and options.is_profile:
            self.profiler = profile.Profile()
            result = self.profiler.runcall(execute, self,transforms,*args, **kwargs)
            self.profiler.dump_stats(options.PROFILE_FILE)
            return result
        else:
            return execute(self, transforms, *args, **kwargs)
    return _

from tornado import web
old_execute = web.RequestHandler._execute
web.RequestHandler._execute = profile_patch(old_execute)