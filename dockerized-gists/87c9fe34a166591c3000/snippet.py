#!/usr/bin/python

# Receive messages from an Azure Event Hub using the Apache Qpid Proton AMQP library.

import sys
import commands
import re
import uuid
import serial
from proton import *

# Device ID
id = uuid.getnode()

# Event Hub address & credentials
# amqps://<keyname>:<key>@<namespace>.servicebus.windows.net/<eventhubname>/ConsumerGroup/<consumergroup>/Partitions/<partition>
# You can find <keyname> and <key> in your Service Bus connection information
# <namespace> is your SB top-level namespace
# <eventhubname> is the name of your Event Hub
# <consumergroup> is the name of an existing Consumer Group; use $Default for the default
# <partition> is a partition ID; a default Event Hub has partitions numbered from 0 to 15

address = "amqps://RootManageSharedAccessKey:92UHxxxx1noKxxxxOkaexxxxyTxoxxxxCePcxxxxIsI=@tomhub-ns.servicebus.windows.net/raspberry/ConsumerGroups/$Default/Partitions/0"

messenger = Messenger()
messenger.subscribe(address)

messenger.start()

while True:
   messenger.recv(1)
   message = Message()
   if messenger.incoming:
      messenger.get(message)
      print(message)

messenger.stop()