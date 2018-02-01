import sys
from kazoo.client import KazooClient

if len(sys.argv) not in (2,3):
    print('Usage: zkDelAll.py [path] [host:port=localhost:2181]')
    exit(1)

host = sys.argv[2] if len(sys.argv) == 3 else 'localhost:2181'
path = sys.argv[1]

tokens = path.split('/')
root = '/'.join(tokens[:-1])+'/'
prefix = tokens[-1]

zk = KazooClient(hosts=host)
zk.start()

for child in zk.get_children(root):
    if child.startswith(prefix):
        child_path = root + child
        print('Deleting ' + child_path)
        zk.delete(child_path)

zk.stop()
