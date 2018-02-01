#!/usr/bin/env python2
############################################################
#  simple script to search for completed torrents in       #
# transmission, notify via pushover and remove the torrent #
# from transmission.									                     #
#                                                          #
#  author: Madson Coelho (madsoncs@gmail.com)              #
#  date: 2014-02-20                                        #
#  name: rsync-mirror                                      #
#  version: 1.0                                            #
############################################################

import urllib
import logging
import httplib
import transmissionrpc

transmission = transmissionrpc.Client('127.0.0.1', port=9091)

### send to pushover function. insert your token and user,
def pushover(msg):
  conn = httplib.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
  urllib.urlencode({
    "token": "",
    "user": "",
    "message": msg,}), { "Content-type": "application/x-www-form-urlencoded" })
  conn.getresponse()

torrents = transmission.get_torrents()
for torrent in torrents:
  if torrent.progress == 100.0:
    pushover('%s: ended!' % torrent.name)
    transmission.remove_torrent(torrent.id)