#!/usr/bin/env python
# -*- coding: utf-8
#
# murmurCollectd.py - "murmur stats (User/Bans/Uptime/Channels)" script for collectd
# Copyright (c) 2015, Nils / 0rokita@informatik.uni-hamburg.de
#
# munin-murmur.py - "murmur stats (User/Bans/Uptime/Channels)" script for munin.
# Copyright (c) 2014, Natenom / natenom@natenom.name
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.
# * Neither the name of the developer nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import collectd
import Ice, sys
import Murmur

#Path to Murmur.ice, this is default for Debian
iceslice='/usr/share/slice/Murmur.ice'

#Includepath for Ice, this is default for Debian
iceincludepath="/usr/share/Ice/slice"

#Murmur-Port (not needed to work, only for display purposes)
serverport=64738

#Port where ice listen
iceport=6502

#Ice Password to get read access.
#If there is no such var in your murmur.ini, this can have any value.
#You can use the values of icesecret, icesecretread or icesecretwrite in your murmur.ini
icesecret="secureme"

#MessageSizeMax; increase this value, if you get a MemoryLimitException.
# Also check this value in murmur.ini of your Mumble-Server.
# This value is being interpreted in kibiBytes.
messagesizemax="65535"

Ice.loadSlice("--all -I%s %s" % (iceincludepath, iceslice))

props = Ice.createProperties([])
props.setProperty("Ice.MessageSizeMax", str(messagesizemax))
props.setProperty("Ice.ImplicitContext", "Shared")
id = Ice.InitializationData()
id.properties = props

ice = Ice.initialize(id)
ice.getImplicitContext().put("secret", icesecret)

meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy("Meta:tcp -h 127.0.0.1 -p %s" % (iceport)))
try:
    server=meta.getServer(1)
except Murmur.InvalidSecretException:
    print 'Given icesecreatread password is wrong.'
    ice.shutdown()
    sys.exit(1)
import time

def dispatch(type_instance, value):
    """
    This function dispatces the value to collectd. The used Name is given
    by type_instance
    :param type_instance: The name of the value for Collectd
    :type type_instance: str
    :param value: The Value to log
    :type value: int
    """
    val = collectd.Values(plugin='murmur')
    val.type = 'gauge'
    val.type_instance = type_instance
    val.values = [value]
    val.dispatch()

def read_callback(data=None):
    """
    The read callback for Collectd. This function gets called on a read from
    collectd.
    """
    #count users
    usersnotauth=0
    users=server.getUsers()
    for key in users.keys():
        if (users[key].userid == -1):
            usersnotauth+=1

    dispatch("users", len(users))
    #dispatch("uptime" float(meta.getUptime())/60/60/24)
    dispatch("chancount",len(server.getChannels()))
    dispatch("bancount", len(server.getBans()))
    dispatch("usersnotauth", usersnotauth)

def shutdown():
    """
    This Function is called on Shutdown by collectd
    """
    ice.shutdown()

# Register the callbacks with collecd
collectd.register_read(read_callback)
collectd.register_shutdown(shutdown)
