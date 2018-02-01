#!/usr/bin/env python
# encoding: utf-8

import asyncio
from aiohttp import request
from lxml import etree
from argparse import ArgumentParser
from os import mkdir, listdir
from execjs import compile as compilejs
from base64 import b64decode
from PIL import Image
from io import BytesIO

@asyncio.coroutine
def name2comic(name: str) -> int:
    print('[name]', name)
    api = 'http://so.u17.com/all/{name}/m0_p1.html'
    res = yield from request('GET', api.format(name=name))
    return int(etree.HTML(
        (yield from res.text())
    ).xpath(
        '//*[@id="comiclist"]/div/div[3]/ul/li/div/div[2]/h3/strong/a'
    )[0].attrib['href'].split('/')[-1].split('.')[0])

@asyncio.coroutine
def comic2chapter(comic_id: int) -> dict:
    print('[comic]', comic_id)
    api = 'http://www.u17.com/comic/ajax.php?mod=comic&act=get_chapters&comic_id={comic_id}'
    res = yield from request('GET', api.format(comic_id=comic_id))
    return (yield from res.json())

@asyncio.coroutine
def chapter2image(chapter_id: int) -> dict:
    print('[chapter]', chapter_id)
    api = 'http://www.u17.com/chapter/{chapter_id}.html'
    res = yield from request('GET', api.format(chapter_id=chapter_id))
    script = [e.text for e in etree.HTML((yield from res.text())).xpath('/html/head/script') if bool(e.text)][-2]
    js = compilejs(
'''var $ = {{
    evalJSON: JSON.parse
}};
{script}'''.format(script=script)
    )
    return js.eval('image_config["image_list"]')

@asyncio.coroutine
def getimage(image_url: bytes, path: str):
    if b'news.u17i.com' in image_url:
        return
    print('[image]', image_url)
    res = yield from request('GET', image_url.decode())
    Image.open(BytesIO((yield from res.read()))).save(path)

@asyncio.coroutine
def main(name:str=None, comic:int=None, chapter:int=None):
    path = {}

    chapter_num = 0
    if not comic and name:
        try:
            comic = yield from name2comic(name)
        except:
            exit("[!] 获取 comic id 出错。")
    path['comic'] = str(comic)
    if not path['comic'] in listdir(): mkdir(path['comic'])

    l = yield from comic2chapter(comic)
    if chapter:
        for i in l:
            if i['chapter_id'] == str(chapter):
                chapter_num = l.index(i)
                break
    for i in l[chapter_num:]:
        path['chapter'] = i['chapter_name']
        if not path['chapter'] in listdir(path['comic']): mkdir('{}/{}'.format(path['comic'], path['chapter']))

        imgs = yield from chapter2image(int(i['chapter_id']))
        yield from asyncio.wait([
            getimage(b64decode(imgs[img]['src']), '{comic}/{chapter}/{img:0>3}.jpg'.format(
                comic = path['comic'],
                chapter = path['chapter'],
                img=img
            )) for img in imgs
        ])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--name', help="漫画名")
    parser.add_argument('--comic', type=int, help="漫画ID")
    parser.add_argument('--chapter', type=int, help="从某章节开始下载")
    args = parser.parse_args()

    if not (args.name or args.comic):
        parser.print_help()
        exit(0)
    asyncio.get_event_loop().run_until_complete(main(args.name, args.comic, args.chapter))
