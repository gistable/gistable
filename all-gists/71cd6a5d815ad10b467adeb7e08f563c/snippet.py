#!/usr/bin/python3
# -*- coding: utf-8 -*-

# USAGE: `$ cat $text_file | python3 gtts-chinese.py`

import os
import sys

from gtts import gTTS


SPECIAL_MAPPING = {
    '0': '零',
    '1': '一',
    '2': '二',
    '3': '三',
    '4': '四',
    '5': '五',
    '6': '六',
    '7': '七',
    '8': '八',
    '9': '九',
    '+': '加',
    '-': '減',
    '*': '乘',
    '/': '除',
    '.': '點',
}


def main():
    sentence = sys.stdin.read().replace(' ', '')
    print(repr(sentence))

    tmp_token = ''
    last_char_is_chinese = False

    for char in sentence:
        print(tmp_token)

        if char in SPECIAL_MAPPING:
            if not last_char_is_chinese and tmp_token:
                tts = gTTS(text=tmp_token, lang='en')
                tts.save("tmp.mp3")
                os.system("mplayer tmp.mp3")
                tmp_token = ''

            tmp_token += SPECIAL_MAPPING[char]
            last_char_is_chinese = True
            continue

        elif ord(char) <= 0x7f:
            # ASCII Table
            if last_char_is_chinese and tmp_token:
                tts = gTTS(text=tmp_token, lang='zh-tw')
                tts.save("tmp.mp3")
                os.system("mplayer tmp.mp3")
                tmp_token = ''

            if char == '\n':
                tmp_token += ' '
                last_char_is_chinese = False
                continue

            if ord('a') <= ord(char) <= ord('z'):
                tmp_token += char
                last_char_is_chinese = False
                continue

            if ord('A') <= ord(char) <= ord('Z'):
                tmp_token += char
                last_char_is_chinese = False
                continue

            continue
        else:
            # consider as Chinese
            if not last_char_is_chinese and tmp_token:
                tts = gTTS(text=tmp_token, lang='en')
                tts.save("tmp.mp3")
                os.system("mplayer tmp.mp3")
                tmp_token = ''

            tmp_token += char
            last_char_is_chinese = True

    else:
        if tmp_token:
            tts = gTTS(text=tmp_token, lang='em')
            tts.save("tmp.mp3")
            os.system("mplayer tmp.mp3")
            tmp_token = ''

    os.system("rm tmp.mp3")


if __name__ == '__main__':
    main()