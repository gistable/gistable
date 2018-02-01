#!usr/bin/python3
# -*- coding: UTF-8 -*-

"""This module is a sample of the OAuth2 authentication by Python3"""

__version__ = "0.1.0"
__author__ = "shin (shin.hateblo.jp)"
__copyright__ = "(C) 2012 shin"
__email__ = "s2pch.luck@gmail.com"
__license__ = "Apache License 2.0"
__status__ = "Prototype"


import configparser
import hashlib
import json
import urllib.parse
import urllib.request
import urllib.error


class OAuth2:
    """This class helps the OAuth2 authentication.
    The configure file whose format is ini(cfg) is needed.
    Some fields are required in the file.
    - authz_endpoint
    - token_endpoint
    - client_id
    - client_secret
    - redirect_uri
    - scope
    Below is a sample.
    ======================
    [DEFAULT]
    authz_endpoint = https://accounts.google.com/o/oauth2/auth
    token_endpoint = https://accounts.google.com/o/oauth2/token
    client_id = [Your Client ID]
    client_secret = [Your Client Secret]
    redirect_uri = urn:ietf:wg:oauth:2.0:oob
    scope = https://www.google.com/reader/atom https://www.google.com/reader/api
    ======================
    """

    AUTHZ_ENDPOINT = "authz_endpoint"
    TOKEN_ENDPOINT = "token_endpoint"
    CLIENT_ID = "client_id"
    CLIENT_SECRET = "client_secret"
    REDIRECT_URI = "redirect_uri"
    SCOPE = "scope"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"

    def __init__(self, configFile="oauth2.ini", additionalSection=None):
        """This is a constructor.
        Arguments:
        configFile -- The config file path
        additionalSection -- If you use an extra section, you can set the name.
        """
        self.configFile = configFile
        self.additionalSection = additionalSection
        self.__initConfiguration() # init self.conf, self.orgConf
        self.__initCacheSection() # init self.cacheSection
        self.accessToken = None
        self.refreshToken = None
        self.__loadCacheTokens()

    def __initConfiguration(self):
        """Load the config file and set to `self.conf`"""
        conf = configparser.ConfigParser()
        with open(self.configFile, "r") as f:
            conf.readfp(f)
        self.orgConf = conf
        # check additionalSection
        adSection = self.additionalSection
        if adSection in conf:
            adSection = conf[adSection]
        self.conf = {}
        for i in [self.CLIENT_ID, self.CLIENT_SECRET, self.AUTHZ_ENDPOINT,
                  self.TOKEN_ENDPOINT, self.REDIRECT_URI, self.SCOPE]:
            if adSection != None and i in adSection:
                self.conf[i] = adSection[i]
            else:
                self.conf[i] = conf["DEFAULT"][i]

    def __initCacheSection(self):
        """Get the hash value for the cache section from authz endpoint and client id"""
        m = hashlib.md5()
        for i in [self.AUTHZ_ENDPOINT, self.CLIENT_ID]:
            m.update(bytes(self.conf[i], "utf-8"))
        self.cacheSection = str(m.hexdigest())

    def __loadCacheTokens(self):
        """Load the tokens from the cache section"""
        with open(self.configFile, "r") as f:
            self.orgConf.readfp(f)
        if not self.cacheSection in self.orgConf:
            return
        t = self.orgConf[self.cacheSection]
        if self.ACCESS_TOKEN in t:
            self.accessToken = t[self.ACCESS_TOKEN]
        if self.REFRESH_TOKEN in t:
            self.refreshToken = t[self.REFRESH_TOKEN]

    def __saveCacheTokens(self):
        """Save the tokens to the cache section"""
        self.orgConf[self.cacheSection] = {
            self.ACCESS_TOKEN: self.accessToken,
            self.REFRESH_TOKEN: self.refreshToken
            }
        with open(self.configFile, "w") as f:
            self.orgConf.write(f)

    def getUrlForAuthCode(self):
        """Get the URL for getting an authorized code.
        This URL is accessed with a web browser.
        Return: URL
        """
        params = {"response_type": "code"}
        for i in [self.CLIENT_ID, self.REDIRECT_URI, self.SCOPE]:
            params[i] = self.conf[i]
        url = "{0}?{1}".format(
            self.conf[self.AUTHZ_ENDPOINT], urllib.parse.urlencode(params))
        return url

    def getAccessToken(self, code=None):
        """Get access token.
        Arguments:
        code -- The authorized code that is got by accessing the URL returned
        from `self.getUrlForAuthCode`. If this is `None`, the current access
        token is returned.
        Return: access token
        """
        if code != None:
            # get access token and request token from the `code`
            params = {"code": code, "grant_type": "authorization_code"}
            for i in [self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI]:
                params[i] = self.conf[i]
            data = urllib.parse.urlencode(params).encode("utf-8")
            request = urllib.request.Request(self.conf[self.TOKEN_ENDPOINT])
            request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
            f = urllib.request.urlopen(request, data)
            root = json.loads(f.read().decode("utf-8"))
            self.accessToken = root[self.ACCESS_TOKEN]
            self.refreshToken = root[self.REFRESH_TOKEN]
            self.__saveCacheTokens()
        return self.accessToken

    def refreshAccessToken(self):
        """Refresh current access token with refresh token
        Return: access token
        """
        params = {"grant_type": "refresh_token",
                  "refresh_token": self.refreshToken}
        for i in [self.CLIENT_ID, self.CLIENT_SECRET]:
            params[i] = self.conf[i]
        data = urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(self.conf[self.TOKEN_ENDPOINT])
        request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        f = urllib.request.urlopen(request, data)
        root = json.loads(f.read().decode("utf-8"))
        self.accessToken = root[self.ACCESS_TOKEN]
        self.__saveCacheTokens()
        return self.accessToken


#---------------------------------

def __main():
    """You can run this test method after preparing the following ini file.
    ======================
    [DEFAULT]
    authz_endpoint = https://accounts.google.com/o/oauth2/auth
    token_endpoint = https://accounts.google.com/o/oauth2/token
    client_id = [Your Client ID]
    client_secret = [Your Client Secret]
    redirect_uri = urn:ietf:wg:oauth:2.0:oob
    scope = https://www.googleapis.com/auth/drive
    ======================
    The client id and client secret can be got from "Google APIs Console".
    Google APIs Console: https://code.google.com/apis/console/
    """


#Makes HTTP request to Google Drive API 'copy' method
    def copyFile(token, target_name):
        print("Access Token: " + token)
        url_destino = "https://www.googleapis.com/drive/v2/files/0AilPd9i9ydNTdFc4a2lvYmZnNkNzSU1kdVFZb0syN1E/copy" \
                      "?key=(YOUR_API_KEY provided by Google API Console)"
        values = "{'title': '%s'}" % target_name
        data = values.encode('utf-8')
        request = urllib.request.Request(url_destino, data, method='POST')
        request.add_header("Authorization", "Bearer " + token)
        request.add_header("Content-Length", len(data))
        request.add_header("Content-Type", "application/json")
        print(request.header_items())
        f = urllib.request.urlopen(request)
        print(f.read())

#Makes HTTP request to Google Drive API 'list' files method
    def listFiles(token):
        print("Access Token: " + token)
        url_destino = "https://www.googleapis.com/drive/v2/files?key=(YOUR_API_KEY provided by Google API Console)"
        request = urllib.request.Request(url_destino)
        request.add_header("Authorization", "Bearer " + token)
        f = urllib.request.urlopen(request)
        print(f.read())


    oauth2 = OAuth2()
    token = oauth2.getAccessToken()
    if token == None:
        print("Input the following URL into your browser and access it!")
        print(oauth2.getUrlForAuthCode())
        code = input("Paste the code ---> ")
        token = oauth2.getAccessToken(code)


    try:
        listFiles(token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            token = oauth2.refreshAccessToken()
            listFiles(token)
        else:
            print(e.code)


    try:
        copyFile(token, 'HiperAgenda_Copiada_3')
    except urllib.error.HTTPError as e:
        if e.code == 401:
            token = oauth2.refreshAccessToken()
            copyFile(token, 'HiperAgenda_Copiada')
        else:
            print(e.code)


if __name__ == "__main__":
    __main()


