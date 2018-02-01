# -*- coding: utf-8 -*-

"""Automatically signing for NetEasy Music"""


import requests


__author__ = 'abrasumente'

REQUEST_URL = 'http://music.163.com/api/point/dailyTask?csrf_token=placeholder&type={}'
TYPE_WEB = 1
TYPE_ANDROID = 0


def nesign(music_u, web=True, android=True):
    """签到

    usage:

        >>> from nesign import nesign
        >>> result = nesign('MY MUSIC_U')
        {'android': {'point': 3, 'code': 200}, 'web': {'point': 2, 'code': 200}}
        >>> result = nesign('MY MUSIC_U') # 错误一般会有一个 msg 字段
        {'android': {'code': -2, 'msg': '重复签到'}, 'web': {'code': -2, 'msg': '重复签到'}}
        >>> result = nesign('一个非法的 MUSIC_U') # 当然也有特例
        {'android': {'code': 301}, 'web': {'code': 301}}


    :type music_u: str
    :param music_u: 你的登陆 token，可以在 web 端下登录后在 music.163.com 域下的 cookies 找到
    :param web: web 端两经验签到
    :param android: android 端三点经验签到

    :rtype: dict
    """
    cookies = {'MUSIC_U': music_u}
    headers = {'Referer': 'http://music.163.com/'}
    result = {}

    if not (web or android):
        raise ValueError('至少指定一种签到类型')

    if web:
        url = REQUEST_URL.format(TYPE_WEB)

        response = requests.post(url, cookies=cookies,
                                 headers=headers)

        result['web'] = response.json()

    if android:
        url = REQUEST_URL.format(TYPE_ANDROID)

        response = requests.post(url, cookies=cookies,
                                 headers=headers)

        result['android'] = response.json()

    return result
