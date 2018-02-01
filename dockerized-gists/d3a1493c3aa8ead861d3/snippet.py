# -*- coding:utf-8 -*-
import pkg_resources
from collections import defaultdict


def add_rdependencies(d, result):
    for r in d.requires():
        result[r.project_name.lower()].add(d)


def add_dependencies(d, result):
    for r in d.requires():
        result[d.project_name.lower()].add(r)


def dump_tree(result, name, indent=0, excludes=["setuptools"]):
    if name.lower() in excludes:
        return
    print(" " * indent, name)
    for sub_d in result[name.lower()]:
        dump_tree(result, sub_d.project_name, indent + 2)


def depth(result, name, n=0):
    if result[name.lower()]:
        n = n + 1
    r = n
    for sub_d in result[name.lower()]:
        tmp = depth(result, sub_d.project_name, n)
        if tmp > r:
            r = tmp
    return r

dependencies = defaultdict(set)
for d in pkg_resources.working_set:
    add_dependencies(d, dependencies)

for d in pkg_resources.working_set:
    print(depth(dependencies, d.project_name))
    dump_tree(dependencies, d.project_name)
    print("-")
