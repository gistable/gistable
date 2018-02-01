#!/usr/bin/env python

import socket
import os
import struct

if getattr(socket, "NETLINK_CONNECTOR", None) is None:
    socket.NETLINK_CONNECTOR = 11

CN_IDX_PROC = 1
CN_VAL_PROC = 1

NLMSG_NOOP = 1
NLMSG_ERROR = 2
NLMSG_DONE = 3
NLMSG_OVERRUN = 4

PROC_CN_MCAST_LISTEN = 1
PROC_CN_MCAST_IGNORE = 2

PROC_EVENT_WHAT = {
    0: "PROC_EVENT_NONE",
    1: "PROC_EVENT_FORK",
    2: "PROC_EVENT_EXEC",
    4: "PROC_EVENT_UID",
    0x40: "PROC_EVENT_GID",
    0x80: "PROC_EVENT_SID",
    0x80000000: "PROC_EVENT_EXIT"
}
PROC_EVENT_NONE = 0

def main():
    # FIXME: Hardcoded structs are not portable
    import platform
    assert platform.processor() == "x86_64"

    # Create Netlink socket
    sock = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM,
                         socket.NETLINK_CONNECTOR)
    sock.bind((os.getpid(), CN_IDX_PROC))

    # Send PROC_CN_MCAST_LISTEN
    data = struct.pack("=IHHII IIIIHH I",
                      16 + 20 + 4, NLMSG_DONE, 0, 0, os.getpid(),
                      CN_IDX_PROC, CN_VAL_PROC, 0, 0, 4, 0,
                      PROC_CN_MCAST_LISTEN)
    if sock.send(data) != len(data):
        raise RuntimeError, "Failed to send PROC_CN_MCAST_LISTEN"

    while True:
        data, (nlpid, nlgrps) = sock.recvfrom(1024)

        # Netlink message header (struct nlmsghdr)
        msg_len, msg_type, msg_flags, msg_seq, msg_pid \
            = struct.unpack("=IHHII", data[:16])
        data = data[16:]

        if msg_type == NLMSG_NOOP:
            continue
        if msg_type in (NLMSG_ERROR, NLMSG_OVERRUN):
            break

        # Connector message header (struct cn_msg)
        cn_idx, cn_val, cn_seq, cn_ack, cn_len, cn_flags \
            = struct.unpack("=IIIIHH", data[:20])
        data = data[20:]

        # Process event message (struct proc_event)
        what, cpu, timestamp = struct.unpack("=LLQ", data[:16])
        data = data[16:]
        if what != PROC_EVENT_NONE:
            # I'm just extracting PID (meaning varies) for example purposes
            pid = struct.unpack("=I", data[:4])[0]
            what = PROC_EVENT_WHAT.get(what, "PROC_EVENT_UNKNOWN(%d)" % what)
            print "%s: CPU%d PID=%d" % (what, cpu, pid)

if __name__ == "__main__":
    main()
