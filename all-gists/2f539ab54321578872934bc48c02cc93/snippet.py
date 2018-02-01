#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asynchat
import asyncore
import logging
import random
import socket
import struct
import time


WAIT_FOR_HEADER = b"\xb2\x02\x00\x00"
WAIT_FOR_MESSAGE = b"\x00"


class MessageProducer(asynchat.simple_producer):

    def __init__(self, data, buffer_size=512):
        asynchat.simple_producer.__init__(self, data, buffer_size)
        self.logger = logging.getLogger('producer')

    def more(self):
        str_msg = asynchat.simple_producer.more(self)
        if str_msg:
            msg = str_msg.encode('utf-8')
            data_length = struct.pack('<I', len(msg) + 9)
            msg_head = data_length + data_length + WAIT_FOR_HEADER
            self.logger.debug("msg_head: %s, msg: '%s'", map(hex, map(ord, msg_head)), msg)
            return msg_head + msg + WAIT_FOR_MESSAGE


class CommentClient(asynchat.async_chat):

    def __init__(self, host, port, room_id, sock, collection=None, rid=None):
        """
        :param sock: client socket
        :param host: server host
        :param port: server port
        :param room_id: room id
        """
        asynchat.async_chat.__init__(self, sock)
        self.logger = logging.getLogger("client")

        self.room_id = room_id
        self.in_buffer = []
        self.data_length = 0
        self.lastest_keepalive = int(time.time())
        self.collection = collection
        self.rid = rid

        self.set_terminator(CommentClient.WAIT_FOR_HEADER)
        self.connect((host, port))
        self.logger.info("host:%s, port:%s, room_id:%s", host, port, room_id)

    def handle_connect(self):
        """
        loginreq
        """
        msg = 'type@=loginreq/username@=visitor{}/password@=1234567890123456/roomid@={}/'.format(
            random.randint(100000, 1000000), self.room_id)
        self.push_with_producer(MessageProducer(msg))

    def handle_close(self):
        self.logger.exception("handle_close")
        self.close()

    def collect_incoming_data(self, data):
        self.logger.debug("incoming data: %s", ":".join("{:02x}".format((ord(c))) for c in data))
        self.logger.debug("incoming data: %s", data)
        self.in_buffer.append(data)

    def writable(self):
        """
        send keep alive every 40s
        :return: True
        """
        now = int(time.time())
        if now - self.lastest_keepalive >= 40:
            msg = "type@=keeplive/tick@={}/".format(now)
            self.push_with_producer(MessageProducer(msg))
            self.lastest_keepalive = now
        return asynchat.async_chat.writable(self)

    def found_terminator(self):
        raw_data = ""
        try:
            raw_data = reduce(lambda x, y: x + str(y), self.in_buffer)
            del self.in_buffer[:]

            terminator = self.get_terminator()
            if terminator == WAIT_FOR_HEADER:
                len1 = struct.unpack("<I", raw_data[-8:-4])[0]
                len2 = struct.unpack("<I", raw_data[:-4])[0]
                if len1 == len2:
                    self.data_length = len1 - 9
                    self.set_terminator(WAIT_FOR_MESSAGE)
                else:
                    self.logger.warning("two data length not same, len1: %d, len2: %d", len1, len2)
            elif terminator == WAIT_FOR_MESSAGE:
                data_length = len(raw_data)
                if self.data_length == data_length:
                    self._process_data(raw_data)
                else:
                    self.logger.warning("data length error, self.data_length: %d, data_length: %d",
                                        self.data_length, data_length)
                self.set_terminator(WAIT_FOR_HEADER)
            else:
                self.logger.warning("unknow terminator %s", map(hex, map(ord, terminator)))
        except:
            self.logger.exception("self.in_buffer: %s, raw_data: %s",
                                  ":".join("{:02x}".format((ord(c))) for c in self.in_buffer),
                                  ":".join("{:02x}".format((ord(c))) for c in raw_data))

    def _process_data(self, raw_data):
        message = {
            "time": int(time.time()),
            "partition_time": time.strftime("%Y-%m-%d")
        }

        # parse raw_data to map
        for tmp in raw_data.split("/"):
            if tmp:
                try:
                    key, value = tmp.split("@=")
                    key = key.replace("@S", "/").replace("@A", "@")
                    value = value.replace("@S", "/").replace("@A", "@")
                    message[key] = value
                except:
                    self.logger.exception("parse data error: %s", tmp)

        # process data according to data["type"]
        try:
            _type = message.get("type")
            if _type == "loginres":
                # joingroup
                if self.rid is None:
                    rid = int(message.get("roomgroup", 0)) + 1
                else:
                    rid = self.rid
                msg = 'type@=joingroup/rid@={}/gid@={}/'.format(self.room_id, rid)
                self.logger.warning("join group: rid: %s", rid)
                self.push_with_producer(MessageProducer(msg))
            elif _type == "keeplive":
                pass
            elif _type in ["chatmsg", "dgb"]:
                self.logger.info("rid:%s, uid:%8s '%s':'%s'",
                                 message["rid"], message["uid"], message["nn"], message.get("txt", "[礼物弹幕]").strip())
                self.put_msg_to_queue(message)
            elif _type in ["uenter", "upgrade", "ranklist", "rss", "srres", "newblackres", "spbc"]:
                self.put_msg_to_queue(message)
            else:
                self.logger.warning(message)
                self.put_msg_to_queue(message)
        except:
            self.logger.exception("raw_data: %s, message: %s", raw_data, message)

    def put_msg_to_queue(self, message):
        if self.collection:
            try:
                self.collection.insert(message)
            except:
                self.logger.exception(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    socket.setdefaulttimeout(30)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    # client = CommentClient("danmu.qietv.douyucdn.cn", 12903, "10002310", sock, None)
    client = CommentClient("openbarrage.douyutv.com", 8601, "230962", sock, None, -9999)
    asyncore.loop(15)


# vim:ai:et:sts=4:sw=4: