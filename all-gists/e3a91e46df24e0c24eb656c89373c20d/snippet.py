#!/usr/bin/env python

import collections
import sys

import lxml.html
import requests
import pyalpm


WIKIPAGE_URL = "https://wiki.archlinux.org/api.php?format=json&action=parse&page=CVE&section=5"


def get_cve_json(url):
    req = requests.get(url)
    req.raise_for_status()
    jsondata = req.json()
    if jsondata:
        jsondata = jsondata["parse"]["text"]["*"]
    return jsondata


def parse_cves(doc_str):
    doc = lxml.html.fromstring(doc_str)
    infos = collections.defaultdict(lambda: collections.defaultdict(list)) # whelp.
    for tr in doc.xpath('//table/tr'):
        tds = tr.xpath('td')
        if len(tds) == 0:
            continue

        texts = [el.text_content().strip() for el in tds]

        cves = filter(lambda x: x.startswith("CVE"), texts[0].split())
        pkgname = texts[1]
        version = texts[3]
        if version == "?" or version == "-":
            version = ""
        version = version.strip(' <=')
        status = texts[6]
        if status.startswith("Invalid") or status.startswith("Not affected"):
            continue
        infos[pkgname][version] += cves
    return infos


def get_vulnerable_pkgs(cve_list):
    alpm_handle = pyalpm.Handle("/", "/var/lib/pacman")
    alpmdb = alpm_handle.get_localdb()

    vulnerables = []
    for pkgname, info in cve_list.items():
        pkg = alpmdb.get_pkg(pkgname)
        if not pkg:
            continue # Not installed

        for cve_version, cves in info.items():
            if pyalpm.vercmp(pkg.version, cve_version) != 1:
                vulnerables.append((pkgname, pkg.version, cves))
    return vulnerables


if __name__ == "__main__":
    print("Downloading CVE wiki page...")
    document = get_cve_json(WIKIPAGE_URL)
    if not document:
        print("Could not fetch CVE list")
        sys.exit(1)

    print("Parsing CVE list...")
    cve_list = parse_cves(document)

    print("Checking CVE list against local PKG DB...")
    vuln_pkgs = get_vulnerable_pkgs(cve_list)
    if len(vuln_pkgs) > 0:
        for pkg, version, cves in vuln_pkgs:
            print("{} {} is vulnerable to {}".format(pkg, version, ', '.join(cves)))
    else:
        print("You're not vulnerable to any CVEs, good job!")
