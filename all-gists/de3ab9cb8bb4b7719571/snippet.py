# coding: utf-8

from objc_util import *
from Foundation import NSBundle

NSBundle.bundleWithPath_('/System/Library/Frameworks/ReplayKit.framework').load()
RPScreenRecorder = ObjCClass('RPScreenRecorder')