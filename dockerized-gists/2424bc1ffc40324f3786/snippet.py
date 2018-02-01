# -*- coding: utf-8 -*-

"""
Python Script to download the Chrome Extensions (CRX) file directly from the google chrome web store.
Referred from http://chrome-extension-downloader.com/how-does-it-work.php
"""

from __future__ import division
import argparse
import requests
import urlparse
import sys

__author__ = 'arul'


class ChromeAppDownloader():
    CRX_URL = "https://clients2.google.com/service/update2/crx?" \
              "response=redirect&prodversion=38.0&x=id%3D~~~~%26installsource%3Dondemand%26uc"
    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
    global headers
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://chrome.google.com",
    }

    def __init__(self):
        pass

    def download(self, _download_url_, _file_name_):
        """
        Download the given URL into given filename.
        :param _download_url_:
        :param _file_name_:
        :return:
        """
        try:
            # Download as Stream
            r = requests.get(url=_download_url_, headers=headers, stream=True)
            redirects = r.history
            if len(redirects) > 0:
                redirect_header = redirects[-1].headers
                if "location" in redirect_header:
                    loc = redirect_header["location"]
                    uparse = urlparse.urlparse(loc)
                    splits = uparse.path.split("/")
                    _fname_ = splits[-1]

            if _fname_:
                _file_name_ = _fname_.replace("extension", _file_name_)
            else:
                _file_name_ += ".crx"

            r_headers = r.headers
            content_length = None
            if "content-length" in r_headers:
                content_length = int(r_headers["content-length"])

            if content_length:
                print "Downloading %s. File Size %s " % (_file_name_, self.byte_to_human(content_length))
            else:
                print "Downloading %s " % _file_name_

            chunk_size = 16 * 1024
            dowloaded_bytes = 0
            with open(_file_name_, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
                    dowloaded_bytes += len(chunk)
                    sys.stdout.write("\r" + self.byte_to_human(dowloaded_bytes))
                    sys.stdout.flush()
        except Exception, e:
            raise ValueError("Error in downloading %s " % _download_url_, e)

    def parse(self, chrome_store_url):
        """
        Validate the given input is chrome store URL or not.
        Returning app ID and app Name from the URL
        :param chrome_store_url:
        :return:
        """
        try:
            # Try to validate the URL
            uparse = urlparse.urlparse(chrome_store_url)
            if uparse.netloc != "chrome.google.com":
                raise ValueError("Not a valid URL %s" % chrome_store_url)
            splits = uparse.path.split("/")
            if not (len(splits) == 4 and uparse.path.startswith("/webstore/detail/")):
                raise ValueError("Not a valid URL %s" % chrome_store_url)
        except Exception, e:
            pass

        return splits[-1], splits[-2]

    def byte_to_human(self, len_in_byte):
        """
        Converts byte into human readable format.
        :param len_in_byte:
        :return:
        """
        in_kb = len_in_byte / 1024
        in_mb = in_kb / 1024
        in_gb = in_mb / 1024

        if in_kb < 1024:
            return "%.2f KB" % in_kb

        if in_mb < 1024:
            return "%.2f MB" % in_mb

        if in_gb > 1:
            return "%.2f GB" % in_gb


if __name__ == '__main__':
    # Getting webstore URL from User
    parser = argparse.ArgumentParser(description='Download CRX file from Google Chrome Webstore.')
    parser.add_argument('-u', '--url', help='URL of the chrome store', required=True)
    args = parser.parse_args()

    downloader = ChromeAppDownloader()
    try:
        file_name = None
        # Validating and building app ID, file name for the given URL
        chrome_app_id, file_name = downloader.parse(chrome_store_url=args.url)
        if chrome_app_id:
            download_url = downloader.CRX_URL.replace("~~~~", chrome_app_id)
            # Downloading the CRX file
            downloader.download(download_url, file_name)
    except Exception, e:
        print e