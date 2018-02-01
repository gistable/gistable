import os
import struct 
import socket

state_table = (
        "EMPTY SLOT",
        "ESTABLISHED",
        "SENT",
        "RECV",
        "WAIT1",
        "WAIT2",
        "WAIT",
        "CLOSE",
        "CLOSE_WAIT",
        "LAST_ACK",
        "LISTEN",
        "CLOSING"
        )


ESTABLISHED = 1
SENT = 2
RECV = 3
WAIT1 = 4
WAIT2 = 5
WAIT = 6
CLOSE = 7
CLOSE_WAIT = 8
LAST_ACK = 9
LISTEN = 10
CLOSING = 11



def decode_addr(name):
    return (socket.inet_ntoa(name[0].decode("hex")[::-1]), 
            struct.unpack(">H", name[1].decode("hex"))[0]) 

def get_tcp():
    f = open("/proc/net/tcp", "r") 
    lines = f.readlines()[1:] 
    f.close() 
    l = []
    for i in lines:
        k = i.strip(" ").split(" ") 
        srcall = k[1].split(":")
        src, srcp = decode_addr(srcall) 
        dstall = k[2].split(":")
        dst, dstp = decode_addr(dstall)
        tx, rx = k[4].split(":") 
        info = {
            "num": k[0],
            "src": src,
            "srcp": srcp,
            "dst": dst,
            "dstp": dstp,
            "state": ord(k[3].decode("hex")),
            "tx": struct.unpack("I", tx.decode("hex"))[0],
            "rx": struct.unpack("I", rx.decode("hex"))[0] 
            } 
        if k[8]:
            info["uid"] = int(k[8])
        if k[16]: 
            info["timeout"] = int(k[16])
        if k[17]: 
            info["inode"] = int(k[17])
        l.append(info)
    return l


def pid_fds():
    table = {}
    for i in os.listdir("/proc"):
        try:
            pid = int(i)
        except:
            continue 
        basej  = "/proc/%s/fd" % i
        fdtable = {}
        try:
            subs = os.listdir(basej)
        except:
            continue
        for j in subs:
            try:
                k = os.readlink("%s/%s" % (basej, j)) 
            except:    
                continue
            fdtable[int(j)] = k
        table[pid] = fdtable
    return table


def inode_to_pid(inode, pid_fds_table):
    for k,v in pid_fds_table.items():
        for i in v.values():
            if inode == i: 
                return k
    return None 


def port_to_pid(port):
    tcpinfo = get_tcp()
    pids_table = pid_fds()
    pid = None
    for i in tcpinfo:
        if "inode" not in i:
            continue  
        if i["srcp"] != port:
            continue 
        pid = inode_to_pid("socket:[%s]" % str(i["inode"]), pids_table)
        if pid:
            break
    return pid



def pid_to_loc(pid):
    f = open("/proc/%d/cmdline" % pid, "r")
    cmdline = f.read().replace("\x00", " ")
    f.close()
    return {
            "cwd": os.readlink("/proc/%d/cwd" % pid),
            "exe": os.readlink("/proc/%d/exe" % pid),
            "cmdline": cmdline
    }


def do_tcp():    
    of = "{:<5}{:<30}{:<30}{:<20}" 
    print of.format("NUM", "SRC", "DST", "STATE")
    for k in get_tcp():
        print of.format(k["num"],
                ":".join((k["src"], str(k["srcp"]))),
                ":".join((k["dst"], str(k["dstp"]))),
                state_table[k["state"]])

def do_port(port): 
    pid = port_to_pid(int(port))
    if not pid:
        print "nothing found"
        return
    print "pid: ", pid
    loc = pid_to_loc(pid)
    print "exe: %s\ncwd: %s\ncmdline: %s" % (loc["exe"], loc["cwd"], loc["cmdline"])


def print_usage():
    print "-p port\t find out which process is binded to this port\n-t Display all tcp connections"

if __name__ == "__main__": 
    import sys
    if len(sys.argv) < 2:
        print_usage()
        exit(0) 
    if sys.argv[1] == "-t": 
        do_tcp()
    elif sys.argv[1] == "-p":
        if len(sys.argv) < 3:
            print_usage()
            exit(0)
        do_port(sys.argv[2])
    else:            
        print_usage()
        