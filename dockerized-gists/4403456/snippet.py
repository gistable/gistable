#!/usr/bin/env python
import sys

from subprocess import Popen, PIPE
from json import loads


class Task(object):
    def __init__(self, data):
        self.data = data
        self.id = data.get('id', None)
        self.uuid = data.get('uuid', None)
        self.status = data.get("status", "completed")

        self.depends = []
        self.rdepends = []

    def get_dotnode(self):
        labels = [
            self.data.get("project", ""),
            self.data.get("description", ""),
        ]

        return r'''
        "%(uuid)s" [
            label = "%(label)s"
            shape = "record"
            color = "%(color)s"
        ]
        ''' % {
            'uuid': self.uuid,
            'label': '|'.join(labels).replace('"', r'\"'),
            'color': "green" if self.status == "pending" else "grey",
        }

    def get_dotname(self):
        return '"%s"' % self.uuid

    def mkedge(self, src, dst, color):
        if src.status != "pending":
            color = "grey"

        return "%s -> %s [color=%s];\n" % (src.get_dotname(),
                                           dst.get_dotname(),
                                           color)

    def dot_deps(self, ignore=None):
        out = self.get_dotnode()

        for dep in self.depends:
            if dep.uuid == ignore:
                continue
            out += self.mkedge(dep, self, 'blue')
            out += dep.dot_deps(ignore=self.uuid)

        for dep in self.rdepends:
            if dep.uuid == ignore:
                continue
            out += self.mkedge(self, dep, 'red')
            out += dep.dot_deps(ignore=self.uuid)

        return out

    def __repr__(self):
        return "<%d: %r>" % (self.id, self.data.get('description', ''))


def get_tasks():
    process = Popen(["task", "export"], stdin=PIPE, stdout=PIPE)
    process.stdin.close()
    tasks = loads('[' + process.stdout.read() + ']')
    return [Task(t) for t in tasks]


def get_task_by_id(id, tasks):
    return [t for t in tasks if t.id == id][0]


def get_task_by_uuid(uuid, tasks):
    return [t for t in tasks if t.uuid == uuid][0]


def make_depends(uuid, tasks):
    t = get_task_by_uuid(uuid, tasks)

    splitted_deps = t.data.get("depends", None)
    if splitted_deps is None:
        splitted_deps = []
    else:
        splitted_deps = splitted_deps.split(",")

    deps = []
    for new_uuid in splitted_deps:
        item = get_task_by_uuid(new_uuid, tasks)
        item.rdepends.append(t)
        deps.append(item)
    t.depends = deps


def main():
    if len(sys.argv) <= 2:
        sys.stderr.write("Usage: %s ID output.png\n" % sys.argv[0])
        sys.exit(1)

    all_tasks = get_tasks()
    [make_depends(t.uuid, all_tasks) for t in all_tasks]
    current = get_task_by_id(int(sys.argv[1]), all_tasks)
    deps = current.dot_deps()
    dot = Popen(["dot", "-Tpng", "-o", sys.argv[2]], stdin=PIPE)
    dot.stdin.write("digraph depends {\n")
    dot.stdin.write("graph [ rankdir=LR, overlap=false ]\n")
    dot.stdin.write(deps)
    dot.stdin.write("\n}")
    dot.stdin.close()
    dot.wait()

if __name__ == '__main__':
    main()