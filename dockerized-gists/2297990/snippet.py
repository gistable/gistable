#!/usr/bin/python
# -*- coding: utf-8 -*-

import chardet


BROTHER_ENCODINGS = [
    ('GB2312', 'GBK', 'GB18030'),
]


def strict_detect(text):
    """
    Detect the encoding of a string strictly,
    if no exact encoding ('decode()' success) was found, an exception will be raise.

    return a str represent of the encoding.
    """
    def get_brothers(ec):
        for i in BROTHER_ENCODINGS:
            if ec in i:
                return i
        return None

    res = chardet.detect(text)

    if res['confidence'] < 1:
        possible_encodings = get_brothers(res['encoding']) or (res['encoding'], )
    else:
        possible_encodings = (res['encoding'], )

    for ec in possible_encodings:
        try:
            text.decode(ec)
        except UnicodeDecodeError:
            pass
        else:
            return ec

    raise DetectionFailed('raw result from chardet: %s' % res)


class DetectionFailed(Exception):
    pass


def convert_string(s, to_ec, from_ec=None):
    """
    convert a string to an indicated encoding,
    if no source encoding was given, try to detect it.
    """
    if not from_ec:
        from_ec = strict_detect(s)
    return s.decode(from_ec).encode(to_ec)


def convert_file(fname, to_ec, from_ec=None, replace=False, to_name=None):
    """
    convert a file to an indicated encoding.

    Arguments::
    :from_ec
        if no source encoding was given, try to detect it.
    :replace
        if replace was set to True, it will cover to_name argument,
        generate a new encoded file to replace the previous one.
    :to_name
        only effective when replace was False,
        if to_name was given, use it as the new file's name,
        if to_name was not given, try to generate a new name based on the old name and encoding.
    """
    if replace:
        to_name = fname
    else:
        if not to_name:
            fname_parts = fname.split('.')
            if len(fname_parts) < 2:
                fpre = fname
                fext = ''
            else:
                fpre = ''.join(fname_parts[:-1])
                fext = fname_parts[-1]
            to_name = '%s_%s.%s' % (fpre, to_ec, fext)

    # print('convert %s to %s from encoding %s to %s')
    # print ('done')

    with open(fname, 'r') as source:
        buf = source.read()
        assert buf, 'file to convert should have content'

    with open(to_name, 'w') as target:
        target.write(convert_string(buf, to_ec, from_ec))


def main():
    import optparse

    parser = optparse.OptionParser(usage='Usage: %prog [options] file_to_convert [, new_file_name]')
    parser.add_option('-f', '--from-ec', type='str',
            help='the original encoding of the file, if not given, detecting will be tried')
    parser.add_option('-t', '--to-ec', type='str', default='utf8',
            help='the output encoding of the new file, if not given, use utf8 as default')
    parser.add_option('-p', '--replace', action='store_true', default=False,
            help='if indicated, the new file will replace the old one, use it carefully')

    options, args = parser.parse_args()
    if len(args) == 1:
        fname = args[0]
        to_name = None
    elif len(args) == 2:
        fname = args[0]
        to_name = args[1]
    else:
        parser.error('incorrect number of arguments, must be one or two')

    convert_file(fname, options.to_ec,
                 from_ec=options.from_ec,
                 replace=options.replace,
                 to_name=to_name)


if __name__ == '__main__':
    main()
