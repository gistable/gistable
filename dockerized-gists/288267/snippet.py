# Copyright (c) 2010, Luca Antiga, Orobix Srl.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
# 
#     * Neither the name of Orobix Srl nor the names of any
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Python implementation of Cocoa NSNotificationCenter

"""

class NotificationCenter(object):

    def __init__(self):
        self.notifications = {}
        self.observerKeys = {}

    def addObserver(self, observer, method, notificationName, observedObject=None):
        if not self.notifications.has_key(notificationName):
            self.notifications[notificationName] = {}
        notificationDict = self.notifications[notificationName] 
        if not notificationDict.has_key(observedObject):
            notificationDict[observedObject] = {}
        notificationDict[observedObject][observer] = method
        if not self.observerKeys.has_key(observer):
            self.observerKeys[observer] = []
        self.observerKeys[observer].append((notificationName,observedObject))

    def removeObserver(self, observer, notificationName=None, observedObject=None):
        try:
            observerKeys = self.observerKeys.pop(observer)
        except KeyError:
            return
        for observerKey in observerKeys:
            if notificationName and observerKey[0] != notificationName:
                continue
            if observedObject and observerKey[1] != observedObject:
                continue
            try:
                self.notifications[observerKey[0]][observerKey[1]].pop(observer)
            except KeyError:
                return
            if len(self.notifications[observerKey[0]][observerKey[1]]) == 0:
                self.notifications[observerKey[0]].pop(observerKey[1])
                if len(self.notifications[observerKey[0]]) == 0:
                    self.notifications.pop(observerKey[0])

    def postNotification(self, notificationName, notifyingObject, userInfo=None):
        try:
            notificationDict = self.notifications[notificationName]
        except KeyError:
            return
        for key in (notifyingObject,None):
            try:
                methodsDict = notificationDict[key]
            except KeyError:
                continue
            for observer in methodsDict:
                if not userInfo:
                    methodsDict[observer](notifyingObject)
                else:
                    methodsDict[observer](notifyingObject,userInfo)


if __name__ == '__main__':

    class A(object):
        def foo(self,notifyingObject,userInfo=None):
            print "foo"
            if userInfo:
                try:
                    print userInfo['bar']
                except KeyError:
                    pass
    
    class B(object):
        pass

    notificationCenter = NotificationCenter()

    a = A()
    b1 = B()
    b2 = B()

    print "Adding observer for notification 'notifyFoo' from b1"
    notificationCenter.addObserver(a,a.foo,"notifyFoo",b1)

    print "Posting from b1"
    notificationCenter.postNotification("notifyFoo",b1)
    print "Posting from b2"
    notificationCenter.postNotification("notifyFoo",b2)
    print "Done posting"

    userInfo = {"bar":"content of userInfo"}

    print "Posting from b1 with userInfo"
    notificationCenter.postNotification("notifyFoo",b1,userInfo)
    print "Posting from b2 with userInfo"
    notificationCenter.postNotification("notifyFoo",b2,userInfo)
    print "Done posting"

    print "Removing observer"
    notificationCenter.removeObserver(a,"notifyFoo")

    print "Adding observer for notification 'notifyFoo' from anyone"
    notificationCenter.addObserver(a,a.foo,"notifyFoo")

    print "Posting from b1"
    notificationCenter.postNotification("notifyFoo",b1)
    print "Posting from b2"
    notificationCenter.postNotification("notifyFoo",b2)
    print "Done posting"

    notificationCenter.removeObserver(a,"notifyFoo")
