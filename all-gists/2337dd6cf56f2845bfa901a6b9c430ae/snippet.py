#!/usr/bin/env python
# -*- coding:utf-8 -*-

from hsdo import make_app
from tornado.testing import AsyncHTTPSTestCase
from tornado.escape import json_encode


class BaseAsyncHTTPSTestCase(AsyncHTTPSTestCase):
    def get_app(self):
        return make_app()

    def simple_test(self, url):
        response = self.fetch(url)
        self.assertNotIn('error_message', json_encode(response.body))
        self.assertEqual(response.code, 200)


class UsersTestCase(BaseAsyncHTTPSTestCase):
    def test_active_users(self):
        self.simple_test('/api/v1/users?status=active')

    def test_new_users(self):
        self.simple_test('/api/v1/users?status=new')


class AdTestCase(BaseAsyncHTTPSTestCase):
    def test_applock_click(self):
        self.simple_test('/api/v1/ad/applock/click')

    def test_applock_show(self):
        self.simple_test('/api/v1/ad/applock/show')

    def test_rate_click(self):
        self.simple_test('/api/v1/ad/rate/click')

    def test_rate_show(self):
        self.simple_test('/api/v1/ad/rate/show')


class FacebookTestCase(BaseAsyncHTTPSTestCase):
    def test_fackbook_enter(self):
        self.simple_test('/api/v1/facebook/enter')


class FeedbackTestCase(BaseAsyncHTTPSTestCase):
    def test_feedback_start(self):
        self.simple_test('/api/v1/feedback/start')


class MenuTestCase(BaseAsyncHTTPSTestCase):
    def test_menu_open(self):
        self.simple_test('/api/v1/menu/open')


class NotifyboxTestCase(BaseAsyncHTTPSTestCase):
    def test_notifybox_enter(self):
        self.simple_test('/api/v1/notifybox/enter')


class ScanTestCase(BaseAsyncHTTPSTestCase):
    def test_scan_start(self):
        self.simple_test('/api/v1/scan/start')


class SdCardScanTestCase(BaseAsyncHTTPSTestCase):
    def test_sdcardscan_start(self):
        self.simple_test('/api/v1/sdcardscan/start')


class SettingTestCase(BaseAsyncHTTPSTestCase):
    def test_setting_start(self):
        self.simple_test('/api/v1/setting/start')

if __name__ == '__main__':
    import unittest
    unittest.main()