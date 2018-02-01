"""
Import hook extending pytz package with usable, generic timezones:
GMT-14 up to GMT+12.

Note that pytz already has Etc/GMT+X timezones, but
(quoting Wikipedia):

"In order to conform with the POSIX style, those zones beginning with "Etc/GMT"
have their sign reversed from what most people expect. In this style,
zones west of GMT have a positive sign and those east have a negative sign."

Because this is insane, we are simply introducing our own zones
that will not have this fatal flaw.
"""
import sys
import imp

import functools
from datetime import timedelta 


class PytzImporter(object):
    """Finder and loader class for the pytz module.
    
    This is the main part of import hook that
    will be executed specifically for pytz when it's
    about to be imported.
    When it happens, we inject our generic timezones
    into all relevant places inside pytz so that they
    can be freely used alongside others.
    """
    def find_module(self, fullname, path=None):
        """Module finding method. It tells Python to use our hook
        only for the pytz package.
        """
        if fullname == 'pytz':
            self.path = path
            return self
        return None
    
    def load_module(self, name):
        """Module loading method. It imports pytz normally
        and then enhances it with our generic timezones.
        """
        if name != 'pytz':
            raise ImportError("%s can only be used to import pytz!",
                              self.__class__.__name__)
        if name in sys.modules:
            return sys.modules[name]    # already imported
        
        file_obj, pathname, desc = imp.find_module(name, self.path)
        try:
            pytz = imp.load_module(name, file_obj, pathname, desc)
        finally:
            if file_obj:
                file_obj.close()
        
        pytz = self.__enhance_pytz(pytz)
        sys.modules[name] = pytz
        return pytz
    
    def __enhance_pytz(self, pytz):
        """Adds support for generic timezones (GMT+X) to pytz module.
        Patch includes changing all_timezones list and set, as well
        as modifying timezone() function.
        """
        generic_tz = self.__get_generic_timezones()
        
        # add to various collections
        pytz.generic_timezones = list(generic_tz.iterkeys())
        pytz.generic_timezones_set = set(generic_tz.iterkeys())
        pytz.all_timezones.extend(generic_tz)
        pytz.all_timezones_set = set(pytz.all_timezones) # has to be recreated
        
        # patch pytz.timezone()
        old__pytz_timezone = pytz.timezone
        @functools.wraps(old__pytz_timezone)
        def pytz_timezone(zone):
            try:
                return old__pytz_timezone(zone)
            except IOError: # when pytz doesn't find match in its data file
                if zone not in pytz.generic_timezones_set:
                    raise
                tz = pytz.FixedOffset(generic_tz[zone])
                pytz._tzinfo_cache[zone] = tz
                return tz
        pytz.timezone = pytz_timezone
        
        return pytz
    
    def __get_generic_timezones(self):
        """Returns dictionary mapping names of our generic
        GMT timezones to their offsets from UTC in minutes.
        """
        span = range(-12, 14 + 1)
        span.remove(0) # pytz alrady has GMT
        return dict(('GMT%(sign)s%(offset)s' % {
                        'sign': '+' if i > 0 else '-',
                        'offset': abs(i),
                     }, timedelta(hours=i).total_seconds() // 60)
                     for i in span)
        
sys.meta_path = [PytzImporter()]