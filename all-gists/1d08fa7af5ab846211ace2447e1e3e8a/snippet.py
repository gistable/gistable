# -*- coding: utf-8 -*-

import weechat

SCRIPT_NAME = 'mockme'
SCRIPT_AUTHOR = 'hikilaka'
SCRIPT_VERSION = '1.0.0'
SCRIPT_LICENSE = 'none'
SCRIPT_DESC = 'Converts your text into a mOcKiNg VeRsIoN'


weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                 SCRIPT_LICENSE, SCRIPT_DESC, '', 'UTF-8')


weechat.hook_command(SCRIPT_NAME, SCRIPT_DESC,
                     '[args]', 'args can be any text.', 'args', 'mockme', '')


wide_symbols = u'！＂＃＄％＆＇（）＊＋，－｡／：；＜＝＞？＠［＼］＾＿｀｛｜｝～'
wide_numbers = u'０１２３４５６７８９'
wide_uppercase = u'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
wide_lowercase = u'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'

wide_characters = wide_symbols + wide_numbers + wide_uppercase + wide_lowercase

normal_symbols = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
normal_numbers = '0123456789'
normal_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
normal_lowercase = 'abcdefghijklmnopqrstuvwxyz'

normal_characters = normal_symbols + normal_numbers + normal_uppercase + normal_lowercase

def normal_to_wide_ch(ch):
    index = normal_characters.find(ch)

    if index is -1:
        return ch

    return wide_characters[index]


def mockme(data, buffer, args):
    result = str()
    cap = False
    wide = False

    input = args.decode('utf-8')

    if not input or (input[0] == '-' and input.find(' ') is -1):
        input = weechat.buffer_get_string(buffer, "input")
        input = input.decode("utf-8")

    if not input:
        return weechat.WEECHAT_RC_OK

    options_stop = input and input[0] == '-' and input.find(' ')
    options = input[1:options_stop] if options_stop else ''
    cmd = ''
    input = input[options_stop:] if options_stop >= 0 else input

    if 'w' in options:
        wide = True
        result = unicode()
    if 'c' in options:
        cmd = '/prism '

    for char in input:
        if cap:
            result += normal_to_wide_ch(char.upper()) if wide else char.upper()
        else:
            result += normal_to_wide_ch(char.lower()) if wide else char.lower()

        if char != ' ':
            cap = not cap

    weechat.command(buffer, cmd + result.encode('utf-8'))
    return weechat.WEECHAT_RC_OK
