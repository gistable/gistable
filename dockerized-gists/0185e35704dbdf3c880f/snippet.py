# -*- encoding: utf-8 -*-
# pip install emoji

import emoji


def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI


def text_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False


if __name__ == '__main__':
    print(char_is_emoji(u'\u2764'))
    print(text_has_emoji(u'I \u2764 emoji'))
