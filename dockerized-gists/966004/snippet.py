#!/usr/bin/env python
#
# Vkontatke OAuth 2.0 wrapper
# Copyright 2011, Adil Khashtamov [adil.khashtamov@gmail.com]
# http://khashtamov.kz
#
#

import logging

import tornado.web
import tornado.escape
from tornado.auth import OAuth2Mixin
from tornado import httpclient

from urllib import urlencode


class VKMixin(OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://api.vkontakte.ru/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "http://api.vk.com/oauth/authorize?"
    _OAUTH_REQUEST_URL = "https://api.vkontakte.ru/method/"

    def get_authenticated_user(self, callback):
        code = self.get_argument("code")
        token = self._oauth_get_consumer_token()
        http = httpclient.AsyncHTTPClient()
        http.fetch(self._oauth_request_token_url(client_id=token["client_id"], code=code,  client_secret=token["client_secret"]), 
                    self.async_callback(self._on_access_token, callback), validate_cert=False)

    def vk_request(self, callback, api_method, params, access_token=None):
        if access_token is None:
            logging.warning("Access token required")
            callback()
            return

        args = {"access_token": access_token}

        if params:
            args.update(params)
        url = self._OAUTH_REQUEST_URL + api_method + ".json?" + urlencode(args)

        http = httpclient.AsyncHTTPClient()
        http.fetch(url, self.async_callback(self._on_vk_request, callback), validate_cert=False)

    def _on_vk_request(self, callback, response):
        if response.error:
            logging.warning("Could not fetch on _on_vk_request")
            #logging.warning(response.error)
            callback(None)
            return
        callback(tornado.escape.json_decode(response.body))

    def _on_access_token(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
            return
        token = self._oauth_parse_response(response.body)

        if token is None:
            logging.warning("access_token is broken")
            callback(None)
            return
        
        access_token = token['access_token'] # get access_token
        uid = token['user_id'] # get uid
        self._oauth_get_user(self.async_callback(self._on_oauth_get_user, access_token, callback), uid=uid, access_token=access_token)
        
    def _oauth_get_user(self, callback, access_token=None, uid=0):
        args = {"uid": uid}
        self.vk_request(api_method="getProfiles", access_token=access_token, params=args, callback=callback)
    
    def _on_oauth_get_user(self, access_token, callback, user):
        if not user:
            raise tornado.web.HTTPError(500, "Auth failed")
            callback(None)
            return
        user["access_token"] = access_token
        callback(user)
        
    def _oauth_get_consumer_token(self):
        self.require_setting("client_secret", "Client OAuth2.0 Secret")
        self.require_setting("client_id", "Client OAuth2.0 ID")
        return dict(
            client_id=self.settings["client_id"],
            client_secret=self.settings["client_secret"])

    def _oauth_parse_response(self, response):
        if response:
            feed = tornado.escape.json_decode(response)
            return feed
        return None