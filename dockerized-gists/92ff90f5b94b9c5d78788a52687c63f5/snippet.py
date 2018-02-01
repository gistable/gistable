#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Get your Steam trading cards by browsing through the Discovery Queue."""

# Makes extensive use of steamweb, see https://github.com/jayme-github/steamweb
# Inspired by /u/zetx's userscript, see https://www.reddit.com/r/Steam/comments/3xvie5/userscript_to_automatically_go_through_a/

# install dependencies: pip3 install --user steamweb

from collections import namedtuple
from steamweb import SteamWebBrowserCfg
from re import search

QUEUES_TO_CRAWL = 3

Item = namedtuple("Item", ["appid", "name"])

def main():
    # initialize Steam web session
    swb = SteamWebBrowserCfg()
    if not swb.logged_in():
        swb.login()
    # work around steamLogin cookie not being sent by steamweb
    login_cookie = [c for c in swb.session.cookies if c.name == "steamLogin"][0]
    login_cookie.domain = "store.steampowered.com"
    swb.session.cookies.set_cookie(login_cookie)
    # start scraping
    sid = get_session_id(swb)
    for i in range(QUEUES_TO_CRAWL):
        print("\n-- Queue #" + str(i + 1) + " --")
        crawl_queue(swb, sid, get_new_queue(swb, sid))

def get_session_id(b):
    """Get the current session ID from the Store page."""
    response = b.get("http://store.steampowered.com/explore/")
    sid_search = search("var g_sessionID = \"([a-z0-9]+)\";",
                        response.text)
    return sid_search.group(1)

def get_new_queue(b, session_id):
    """Request another Discovery Queue from the Steam Store.

    Return a list of (appid, name) tuples."""
    data = {
        "sessionid": session_id,
        "queuetype": "0"
    }
    js = b.post("http://store.steampowered.com/explore/generatenewdiscoveryqueue",
                data=data).json()
    items = []
    for appid in js["queue"]:
        items.append(Item(appid=appid, name=js["rgAppData"][str(appid)]["name"]))
    return items

def crawl_queue(b, session_id, items):
    """Send POST requests to clear items from the given queue."""
    ls = str(len(items))
    # going one-by-one, could do asynchronously, but probably not a big deal
    for n, item in enumerate(items):
        url = "http://store.steampowered.com/app/" + str(item.appid)
        post_data = {
            "sessionid": session_id,
            "appid_to_clear_from_queue": str(item.appid)
        }
        print("(" + str(n + 1) + "/" + ls + ") " + item.name + " : " + url)
        b.post(url, data=post_data)

if __name__ == "__main__":
    main()