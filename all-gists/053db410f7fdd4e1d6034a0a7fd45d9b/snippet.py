#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import requests
import sys
from Crypto.Cipher import AES


def decrypt(data, key, iv):
    """Decrypt using AES CBC"""
    decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    return decryptor.decrypt(data)


def get_binary(url):
    """Get binary data from URL"""
    data = ''
    for chunk in requests.get(url, stream=True):
        data += chunk
    return data


def main(filename, output_folder, skip_ad=True):
    """Main"""
    with open(filename, 'r') as f:
        data = f.read()
    # make output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # download and decrypt chunks
    for part_id, sub_data in enumerate(data.split('#UPLYNK-SEGMENT:')):
        # skip ad
        if skip_ad:
            if re.findall('#UPLYNK-SEGMENT:.*,.*,ad', '#UPLYNK-SEGMENT:' + sub_data):
                continue
        # get key, iv and data
        chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)\s.*\s(.*)', sub_data)
        for chunk in chunks:
            key_url = chunk[0]
            iv_val = chunk[1][2:]
            data_url = chunk[2]
            file_name = os.path.basename(data_url).split('?')[0]
            print('Processing "%s"' % file_name)
            # download key and data
            key = get_binary(key_url)
            enc_data = get_binary(data_url)
            iv = iv_val.decode('hex')
            # save decrypted data to file
            out_file = os.path.join(output_folder, '%s' % file_name)
            with open(out_file, 'wb') as f:
                dec_data = decrypt(enc_data, key, iv)
                f.write(dec_data)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Usage: %s <m3u8_file> <out_folder>' % os.path.basename(sys.argv[0]))
    main(sys.argv[1], sys.argv[2], skip_ad=True)
