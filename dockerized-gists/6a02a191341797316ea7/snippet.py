import os
import time

# Config
NAME = ["Steven Kafshaz"]

LASTMSG = {}

def filesbychannel(dirlist):
    out = {}
    for a in dirlist:
        if a.split("_")[0] in out:
            out[a.split("_")[0]].append(a)
        else:
            out[a.split("_")[0]] = [a]
    return out

def open_log(channel):
    out = {"id": 0, "name": "", "listener": "", "started": "", "topic": "", "lines": []}
    with open(channel[-1], "rb") as f:
        a = f.read().decode("utf_16").split("\n")
    out["id"] = int(a[6].split()[-1])
    out["name"] = a[7].split()[-1]
    out["listener"] = a[8].split()[-1]
    out["topic"] = " > ".join(a[12].split(" > ")[1:]).strip()
    out["lines"] = [parse_line(b.strip()) for b in a[13:]][:-1]
    return out

def parse_line(line):
    out = {"timestamp": "", "fromusr": "", "text": ""}
    try:
        ts = " ".join(line.split(" ")[1:3])
        out["timestamp"] = int(time.mktime(time.strptime(ts, "%Y.%m.%d %H:%M:%S")))
        out["fromusr"] = line.split(" ] ")[1].split(" > ")[0].strip()
        out["text"] = line.split(" > ")[1].strip()
        return out
    except (IndexError,ValueError):
        return None

def match(text):
    return NAME[0] in text
    out = {}
    for a in NAME:
        out[a] = a in text
    return out

"""
def main():
    while True:
        channels = filesbychannel(os.listdir("."))
        for ch in channels:
            l = open_log(channels[ch])
            LATEST[ch] = 
        
        time.sleep(1)
"""