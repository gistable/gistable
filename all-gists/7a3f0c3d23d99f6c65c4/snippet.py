#!/bin/python
import requests
import multiprocessing
import uuid
import time

def worker():
    while True:
        req = requests.post("http://uvb.csh.rit.edu/register/rhubarb_%s" % uuid.uuid4())
        time.sleep(1)
    return

if __name__ == "__main__":
    jobs = []
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
    for j in jobs:
        j.join()
