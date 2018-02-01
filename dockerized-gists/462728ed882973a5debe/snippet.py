#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Xue Can <xuecan@gmail.com> and contributors.

"""
Python Project Compiler
=======================

本程序用于将目录 src 中的内容复制到目录 dst 中，如果在 src 中包含 .py
文件，将会使用 py_compile 模块编译为 .pyc 后再复制，并忽略原 .py 文件。
"""

import os
import sys
import shutil
import re
import subprocess


_KEEP_PATTERS = []
_IGNORE_PATTERNS = [re.compile(r"^\.")]
_PATHS = {}


def should_ignore(name):
    for pattern in _KEEP_PATTERS:
        if pattern.match(name):
            return False
    for pattern in _IGNORE_PATTERNS:
        if pattern.match(name):
            return True
    return False


def parse_args(args):
    cwd = os.path.abspath(os.getcwd())
    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    if not dst.startswith(cwd):
        raise ValueError(u"目标目录不在当前目录中")
    if dst.startswith(src):
        raise ValueError(u"目标目录位于源目录中")
    if os.path.exists(dst):
        if not os.path.isdir(dst):
            raise RuntimeError(u"目标路径已存在但不是目录")
    _PATHS["src"] = src
    _PATHS["dst"] = dst
    if subprocess.check_output([args.python, "-c", "print('python')"])[:6] != "python":
        raise ValueError("请指定有效 Python 可执行文件")
    _PATHS["python"] = args.python
    if args.keep:
        for item in args.keep:
            _KEEP_PATTERS.append(re.compile(item))
    if args.ignore:
        for item in args.ignore:
            _IGNORE_PATTERNS.append(re.compile(item))
    if args.clean:
        if os.path.exists(dst):
            shutil.rmtree(dst)


def get_dst_path(src):
    if not src.startswith(_PATHS["src"]):
        raise ValueError("src 不在源目录中")
    return src.replace(_PATHS["src"], _PATHS["dst"], 1)


def compile_file(filename):
    command = [_PATHS["python"], "-m", "py_compile", filename]
    subprocess.call(command)


def copy_or_compile():
    for dirpath, dirnames, filenames in os.walk(_PATHS["src"], topdown=True):
        # (1)
        ignore_indexes = list()
        for index in range(len(dirnames)):
            if should_ignore(dirnames[index]):
                ignore_indexes.insert(0, index)
        for index in ignore_indexes:
            dirnames.pop(index)
        # (2)
        try:
            os.mkdir(get_dst_path(dirpath))
        except OSError, e:
            pass
        # (3)
        for filename in filenames:
            if should_ignore(filename)\
              or filename.endswith(".pyc")\
              or filename.endswith(".pyo"):
                pass
            else:
                src = os.path.join(dirpath, filename)
                if filename.endswith(".py"):
                    compile_file(src)
                    src = src[:-(len(".py"))] + ".pyc"
                dst = get_dst_path(src)
                shutil.copy(src, dst)


if __name__ == "__main__":
    import argparse
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(
        description=u"Python Project Compiler"
    )
    parser.add_argument("src", help=u"源目录")
    parser.add_argument("dst", help=u"目标目录")
    parser.add_argument("--clean", action='store_true',
                        help=u"是否重建目标目录")
    parser.add_argument("--python", default=sys.executable,
                        help=u"指定用于编译的 python 路径")
    parser.add_argument("--ignore", action='append',
                        help=u"需要被忽略的目录名或文件名")
    parser.add_argument("--keep", action='append',
                        help=u"不被忽略的目录名或文件名")
    args = parser.parse_args()
    parse_args(args)
    copy_or_compile()
