#!/usr/bin/env python3
from argparse import ArgumentParser
from multiprocessing import Process
from threading import Thread
from curio import run, spawn, sleep
from curio.socket import socket
from curio.socket import (AF_INET, SOCK_DGRAM, IPPROTO_UDP,
                          SOL_SOCKET, SO_REUSEADDR,
                          gethostbyname, gethostname)
from os import getpid, getppid
from asyncio_extras import async_contextmanager

MESSAGE = ('H {hostname:^15} P/PID {pid}/{ppid} '
           'P {process_id}/{num_processes} '
           'T {thread_id}/{num_threads} '
           'C {coroutine_id}/{num_coroutines}').format

@async_contextmanager
async def network(address, peers):
    async def send(message):
        await sock.sendto(message.encode(), (host, port))
        for peer_addr in resolved_peers:
            await sock.sendto(message.encode(), peer_addr)

    async def recv():
        return (await sock.recv(2048)).decode()

    host, port = address
    ip = await gethostbyname(host)
    resolved_peers = [(await gethostbyname(peer_host), peer_port)
                      for peer_host, peer_port in peers]
    async with socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((ip, port))
        yield send, recv

async def coroutine(*args, **kwargs):
    async def send_task():
        while True:
            await sleep(.1)
            msg = MESSAGE(**kwargs, hostname=hostname, pid=getpid(), ppid=getppid())
            await send(msg)

    async def recv_task():
        while True:
            msg = await recv()
            print(msg)

    address, peers = kwargs['address'], kwargs['peers']
    hostname = await gethostname()
    async with network(address, peers) as (send, recv):
        tasks = [await spawn(send_task()),
                 await spawn(recv_task())]
        for t in tasks:
            await t.join()

def thread(*args, **kwargs):
    num = kwargs['num_coroutines']
    pool = [coroutine(*args, **kwargs, coroutine_id=coroutine_id)
            for coroutine_id in range(1, num+1)]
    async def task():
        for c in pool:
            await spawn(c)
    run(task())

def process(*args, **kwargs):
    num = kwargs['num_threads']
    pool = [Thread(target=thread, args=args,
                   kwargs={**kwargs, 'thread_id': thread_id})
            for thread_id in range(1, num+1)]
    for t in pool:
        t.start()
    for t in pool:
        t.join()

def main(*args, **kwargs):
    num = kwargs['num_processes']
    pool = [Process(target=process, args=args,
                    kwargs={**kwargs, 'process_id': process_id})
            for process_id in range(1, num+1)]
    for p in pool:
        p.start()
    for p in pool:
        p.join()

def address(s='', default_host='0.0.0.0', default_port=5959):
    if not s:
        return default_host, default_port
    if ':' not in s:
        return s, default_port
    host, port = s.rsplit(':', 1)
    return host, int(port)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p',    dest='num_processes',  type=int, default=2)
    parser.add_argument('-t',    dest='num_threads',    type=int, default=2)
    parser.add_argument('-c',    dest='num_coroutines', type=int, default=2)
    parser.add_argument('-a',    dest='address',        type=address, default=address())
    parser.add_argument('peers', nargs='*',             type=address)
    args = parser.parse_args()

    main(*args._get_args(), **dict(args._get_kwargs()))
