# -*- coding: utf-8 -*-
# 14-8-20
# create by: snower

import os
import time
import multiprocessing
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class RotatingFileHandler(RotatingFileHandler):
    lock=multiprocessing.Lock()
    version=multiprocessing.Value("i",0)

    def __init__(self, *args, **kwargs):
        super(RotatingFileHandler, self).__init__(*args, **kwargs)

        self._version = 0

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        with self.__class__.lock:
            if self._version == self.__class__.version.value:
                if self.backupCount > 0:
                    for i in range(self.backupCount - 1, 0, -1):
                        sfn = "%s.%d" % (self.baseFilename, i)
                        dfn = "%s.%d" % (self.baseFilename, i + 1)
                        if os.path.exists(sfn):
                            #print "%s -> %s" % (sfn, dfn)
                            if os.path.exists(dfn):
                                os.remove(dfn)
                            os.rename(sfn, dfn)
                    dfn = self.baseFilename + ".1"
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    # Issue 18940: A file may not have been created if delay is True.
                    if os.path.exists(self.baseFilename):
                        os.rename(self.baseFilename, dfn)
                self.__class__.version.value += 1
            self._version += 1

        if not self.delay:
            self.stream = self._open()

class TimedRotatingFileHandler(TimedRotatingFileHandler):
    lock=multiprocessing.Lock()
    version=multiprocessing.Value("i",0)

    def __init__(self,*args,**kwargs):
        super(TimedRotatingFileHandler,self).__init__(*args,**kwargs)

        self._version = 0

    def rename_file(self):
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            #s = glob.glob(self.baseFilename + ".20*")
            #if len(s) > self.backupCount:
            #    s.sort()
            #    os.remove(s[0])
            for s in self.getFilesToDelete():
                os.remove(s)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        with self.__class__.lock:
            if self.__class__.version.value==self._version:
                self.rename_file()
                self.__class__.version.value+=1
            self._version+=1

        #print "%s -> %s" % (self.baseFilename, dfn)
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt