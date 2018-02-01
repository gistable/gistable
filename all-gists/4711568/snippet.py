#! /usr/bin/env python# -*- coding: utf-8 -*-

import urllib
import zipfile
import json
import re
import os
from github import Github

GITHUB_TOKEN = "Enter Your GitHub Token"
SEARCH_KEYWORD = "twitter oauth"
LANGUAGE       = "Python"
OUTPUT_PATH    = "./index.txt"
ZIP_PATH       = "./zip/"

banList = ["__init__", "__repr__", "get", "main", "open", "write", "read", "close", "loop", "clear"]

def downloadZipBall(name, url):
    if not os.path.exists(ZIP_PATH):
        os.mkdir(ZIP_PATH)
    path = ZIP_PATH + name + ".zip"
    urllib.urlretrieve(url, path)
    return path

def fetchDefFromZip(path):
    zf = zipfile.ZipFile(path, 'r')
    for f in zf.namelist():
        if f[len(f) - 3:] == ".py":
            return extractDef(zf.read(f), f[f.index("/"):])
    return None

def extractDef(fileStr, path):
    defInfo = []
    r = re.compile('def .*?:')
    lines = fileStr.split("\n")
    for (i, line) in enumerate(lines):
        line = line.strip()
        m = r.match(line)
        if m:
            name = line.replace("def ", "")
            name = name[:name.index("(")]
            name = name.strip()
            if name in banList: continue
            defInfo.append({"line" : i + 1, "name" : name, "path" : path})
    return defInfo

def writeIndexFile(repos, defInfo):
    if defInfo == None or len(defInfo) == 0:
        return
    f = open(OUTPUT_PATH, "a")
    output = {
            'id'          : repos.id,
            'name'        : repos.name,
            'full_name'   : repos.full_name,
            'description' : repos.description,
            'url'         : repos.url,
            'git_url'     : repos.git_url,
            'clone_url'   : repos.clone_url,
            'homepage'    : repos.homepage,
            'language'    : repos.language,
            'match'       : defInfo
            }

    str = json.dumps(output)
    f.write(str + "\n")
    f.close()

def createIndex():
    g = Github(GITHUB_TOKEN)

    for repos in g.legacy_search_repos(SEARCH_KEYWORD, LANGUAGE):
        if repos.private: continue
        if not repos.has_downloads: continue
        if repos.fork: continue

        print repos.name
        try:
            link    = repos.get_archive_link("zipball")
            path    = downloadZipBall(repos.name, link)
            defInfo = fetchDefFromZip(path)
            writeIndexFile(repos, defInfo)
        except:
            pass

if __name__ == '__main__':
    createIndex()

