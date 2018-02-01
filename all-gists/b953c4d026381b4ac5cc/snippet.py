#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @file     curl_request.py
# @author   kaka_ace <xiang.ace@gmail.com>
# @date     Jan 10 2015
# @breif    learn from human_curl 
# @refrences:
#      http://pycurl.sourceforge.net/doc/curlmultiobject.html
#      http://curl.haxx.se/libcurl/c/curl_multi_info_read.html
#      http://stackoverflow.com/questions/5809033/multi-request-pycurl-running-forever-infinite-loop 
#      http://stackoverflow.com/questions/15724117/how-can-i-get-the-response-body-from-pycurl-multi-curl-requests


import sys
import json
import httplib
from string import capwords
import requests

try:
    import pycurl2 as pycurl
except ImportError:
    import pycurl
from io import BytesIO

import human_curl


class RequestError(Exception):
    pass


class InvalidMethod(Exception):
    pass


class CurlError(Exception):
    """Exception raise when `pycurl.Curl` raise connection errors

    :param code: HTTP error integer error code, e. g. 404
    :param message: error message string
    """
    def __init__(self, code, message=None):
        self.code = code
        message = message or httplib.responses.get(code, "Unknown")
        Exception.__init__(self, "%d: %s" % (self.code, message))


class CaseInsensitiveDict(dict):
    """Case-insensitive Dictionary

    For example, `headers['content-encoding']` will return the
    value of a `'Content-Encoding'` response header.
    """

    def __init__(self, *args, **kwargs):
        tmp_d = dict(*args, **kwargs)
        super(CaseInsensitiveDict, self).__init__([(k.lower(), v) for k, v in tmp_d.iteritems()])

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __delitem__(self, key):
        super(CaseInsensitiveDict, self).__delitem__(key.lower())

    def __contains__(self, key):
        return key.lower() in self

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(key.lower())

    def iteritems(self):
        return ((capwords(k, '-'), v) for k, v in super(CaseInsensitiveDict, self).iteritems())


class KKRequest(object):
    _curl_options = {
        "GET": pycurl.HTTPGET,
        "POST": pycurl.POST,
        "PUT": pycurl.PUT,
        "HEAD": pycurl.NOBODY,
    }

    SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PUT", "OPTIONS")

    _multi_curl = pycurl.CurlMulti()
    _multi_curl_map = {}
    _multi_curl_request_info = []

    @classmethod
    def http_do_request(cls, method, url, headers = None, data = None, of = None, session=None):
        try:
            if session is None:
                session = requests.Session()
            response = session.request(method, url, headers=headers, timeout=120)
            content = (response.status_code, response.content)
            return content
        except Exception as e:
            error_msg = str(e).split(' ')
            content = (-1, error_msg)
            return content

    @classmethod
    def make_pycurl(cls, method, url, headers = None, data = None):
        header_output = BytesIO()
        body_output = BytesIO()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.NOSIGNAL, 1)

        if isinstance(headers, dict):
            c.setopt(pycurl.HTTPHEADER, ["%s: %s" % (capwords(f, "-"), v) for f, v
                    in CaseInsensitiveDict(headers).iteritems()])

        c.setopt(pycurl.CONNECTTIMEOUT, 3)
        c.setopt(pycurl.TIMEOUT, 3)

        if method in cls._curl_options.keys():
            c.setopt(cls._curl_options[method], True)
        elif method in cls.SUPPORTED_METHODS:
            c.setopt(pycurl.CUSTOMREQUEST, method)

        if method in ("POST", "PUT"):
            if data is None:
                data = ""

            body_inout = BytesIO(data)
            c.setopt(pycurl.READFUNCTION, body_inout.read)
            def ioctl(cmd):
                if cmd == pycurl.IOCMD_RESTARTREAD:
                    body_inout.seek(0)

            c.setopt(pycurl.IOCTLFUNCTION, ioctl)
            if method == "PUT":
                c.setopt(pycurl.PUT, True)
                c.setopt(pycurl.INFILESIZE, len(data))
            else:
                c.setopt(pycurl.POST, True)
                c.setopt(pycurl.POSTFIELDSIZE, len(data))

            c.setopt(pycurl.HEADERFUNCTION, header_output.write)
            c.setopt(pycurl.HEADERFUNCTION, body_output.write)

        return (c, header_output, body_output)

    @classmethod
    def http_do_request_by_curl(cls, method, url, headers = None, data = None):
        method = method.upper()
        if method not in cls.SUPPORTED_METHODS:
            raise InvalidMethod("cURL do not support %s method" % method.upper())

        try:
            c, header_output, body_output = cls.make_pycurl(method, url, headers, data)

            c.perform()
        except pycurl.error, e:
            error_message = "pycurl error: %s" % str(e)
            return (-1, error_message)
        except Exception, e:
            error_message = "Request Error: %s" % str(e)
            return (-1, error_message)
        else:
            status_code = int(c.getinfo(pycurl.HTTP_CODE))
            content = body_output.getvalue()
            return (status_code, content)

    @classmethod
    def reset_http_multi_curl(cls):
        cls._multi_curl_request_info = []

        for curl_id in cls._multi_curl_map:
            c, _, _ = cls._multi_curl_map[curl_id]
            cls._multi_curl.remove_handle(c)

        cls._multi_curl_map = {}

    @classmethod
    def add_http_multi_requests_for_pycurl(cls, method, url, headers = None, data = None):
        method = method.upper()
        if method not in cls.SUPPORTED_METHODS:
            raise InvalidMethod("cURL do not support %s method" % method.upper())

        cls._multi_curl_request_info.append((method, url, headers, data))

    @classmethod
    def send_http_multi_request_by_curl(cls):
        if len(cls._multi_curl_request_info) == 0:
            return None, None

        for request_info in cls._multi_curl_request_info:
            method, url, headers, data = request_info
            try:
                c, header_output, body_output = cls.make_pycurl(method, url, headers, data)
            except Exception, e:
                # ignore the current method
                print "make pycurl request failed, but ignore the request info %s" % request_info
            else:
                cls._multi_curl_map[id(c)] = (c, header_output, body_output)
                cls._multi_curl.add_handle(c)

        response_sucess_list = []
        response_error_list = []

        curl_processed_count = 0
        curl_total = len(cls._multi_curl_map)

        while curl_processed_count < curl_total:
            while True:
                ret, curl_count = cls._multi_curl.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            print ret
            print curl_count

            queue_num, success_list, error_list = cls._multi_curl.info_read()
            print queue_num
            print len(success_list)
            print len(error_list)

            for c in success_list:
                c, header_output, body_output = cls._multi_curl_map[id(c)]
                status_code = int(c.getinfo(pycurl.HTTP_CODE))
                content = body_output.getvalue()
                response_sucess_list.append((status_code, content))

                if id(c) in cls._multi_curl_map:
                    cls._multi_curl_map.pop(id(c))

                cls._multi_curl.remove_handle(c)

            for c, error_num, error_message in error_list:
                message = "request faield: %d %s" % (error_num, error_message)
                response_error_list.append((-1, message))

                if id(c) in cls._multi_curl_map:
                    cls._multi_curl_map.pop(id(c))

                cls._multi_curl.remove_handle(c)

            curl_processed_count = curl_processed_count + len(success_list) + len(error_list)

            cls._multi_curl.select(1.0)

        cls.reset_http_multi_curl()

        return response_sucess_list, response_error_list

#status_code, content = KKRequest.http_do_request_by_curl("POST", "http://192.168.0.29", headers=None, data="hello")
#print status_code
#print content
#print '---------------------'


for i in range(10):
    KKRequest.add_http_multi_requests_for_pycurl("GET", "http://www.baidu.com", headers=None, data="hello")

s, e = KKRequest.send_http_multi_request_by_curl()
print '---------------------'
print s
print '---------------------'
print e









