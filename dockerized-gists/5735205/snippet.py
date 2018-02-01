import cProfile
import os
import pstats
import time
from datetime import datetime
from functools import wraps
from io import StringIO
from logging import getLogger

logger = getLogger(__name__)


def label(code):
    if isinstance(code, str):
        return ('~', 0, code)  # built-in functions ('~' sorts at the end)
    else:
        return '%s %s:%d' % (code.co_name,
                             code.co_filename,
                             code.co_firstlineno)


class KCacheGrind(object):
    def __init__(self, profiler):
        self.data = profiler.getstats()
        self.out_file = None

    def output(self, out_file):
        self.out_file = out_file
        self.out_file.write('events: Ticks\n')
        self._print_summary()
        for entry in self.data:
            self._entry(entry)

    def _print_summary(self):
        max_cost = 0
        for entry in self.data:
            totaltime = int(entry.totaltime * 1000)
            max_cost = max(max_cost, totaltime)
        self.out_file.write('summary: %d\n' % (max_cost,))

    def _entry(self, entry):
        out_file = self.out_file

        code = entry.code
        # print >> out_file, 'ob=%s' % (code.co_filename,)
        if isinstance(code, str):
            out_file.write('fi=~\n')
        else:
            out_file.write('fi=%s\n' % (code.co_filename,))
        out_file.write('fn=%s\n' % (label(code),))

        inlinetime = int(entry.inlinetime * 1000)
        if isinstance(code, str):
            out_file.write('0  %s\n' % inlinetime)
        else:
            out_file.write('%d %d\n' % (code.co_firstlineno, inlinetime))

        # recursive calls are counted in entry.calls
        if entry.calls:
            calls = entry.calls
        else:
            calls = []

        if isinstance(code, str):
            lineno = 0
        else:
            lineno = code.co_firstlineno

        for subentry in calls:
            self._subentry(lineno, subentry)
        out_file.write("\n")

    def _subentry(self, lineno, subentry):
        out_file = self.out_file
        code = subentry.code
        # out_file.write('cob=%s\n' % (code.co_filename,))
        out_file.write('cfn=%s\n' % (label(code),))
        if isinstance(code, str):
            out_file.write('cfi=~\n')
            out_file.write('calls=%d 0\n' % (subentry.callcount,))
        else:
            out_file.write('cfi=%s\n' % (code.co_filename,))
            out_file.write('calls=%d %d\n' % (subentry.callcount, code.co_firstlineno))

        totaltime = int(subentry.totaltime * 1000)
        out_file.write('%d %d\n' % (lineno, totaltime))


def profiled(func, prof_path='/tmp'):
    """
    This will dump a file in `prof_path` with the kcachegrind
    profile and emmit a basic simple stats dump on the logger
    (in case you don't have kcachegrind installed).

    The name for the file is in this format:

        <module name>.<func name>.<duration>.<timestamp>.prof
    """

    @wraps(func)
    def profiled_wrapper(*args, **kwargs):
        profid = "%s.%s" % (func.__module__, func.__name__)

        profname = "%s.%d.prof" % (profid, time.time())
        profname = os.path.join(prof_path, profname)

        prof = cProfile.Profile()
        start = datetime.now()
        try:
            return prof.runcall(func, *args, **kwargs)
        finally:

            # seeing how long the request took is important!
            elap = datetime.now() - start
            elapms = elap.seconds * 1000.0 + elap.microseconds / 1000.0
            kg = KCacheGrind(prof)
            with open(profname, 'w') as pf:
                kg.output(pf)

            profname2 = "%s.%06dms.%d.prof" % (profid, elapms, time.time())
            profname2 = os.path.join(prof_path, profname2)
            os.rename(profname, profname2)
            logger.critical("KCacheGrind ready dump saved to: %s", profname2)

            stats = pstats.Stats(prof, stream=StringIO())
            stats.strip_dirs()
            stats.sort_stats(1)  # sort by time
            stats.print_stats()
            logger.critical(
                "Profile results for %s(*%s, **%s): %s",
                profid, args, kwargs, stats.stream.getvalue(),
            )

    return profiled_wrapper
