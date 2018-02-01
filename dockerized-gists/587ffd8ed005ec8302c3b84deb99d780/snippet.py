#!/usr/bin/env python
# -*- coding: utf-8 -*-


def load_gist(gist_id):
    """translate Gist ID to URL"""
    from json import load
    from urllib import urlopen

    gist_api = urlopen("https://api.github.com/gists/" + gist_id)

    files = load(gist_api)["files"]
    files_head_member = files.keys()[0]
    raw_url = files[files_head_member]["raw_url"]

    gist_src = urlopen(raw_url).read()
    return gist_src


def import_from_gist(gist_id):
    """import from Gist"""
    from sys import path
    from tempfile import mkdtemp

    gist_src = load_gist(gist_id)
    temp_dir = mkdtemp()
    path.append(temp_dir)
    with open(temp_dir + "/module{}.py".format(gist_id), "w") as f:
        f.write(gist_src)

    exec "import module{} as mod".format(gist_id)
    return mod


if __name__ == "__main__":
    gist_id = "55b8bec6e652c860f287288d98bc507f"
    mod = import_from_gist(gist_id)
    mod.hello()
