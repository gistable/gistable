from selenium import webdriver

from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.remote.command import Command

class PersistentWebdriver (webdriver.Remote):
    
    def __init__(self, session_id=None, browser_name=''):
        command_executor='http://localhost:4444/wd/hub'
        platform = version = ''
        javascript_enabled = True

        self.command_executor = command_executor
        if type(self.command_executor) is str:
            self.command_executor = RemoteConnection(command_executor)
        
        self.command_executor._commands['GET_SESSION'] = ('GET', '/session/$sessionId')
        
        self.session_id = session_id
        self.capabilities = {}
        self.error_handler = ErrorHandler()

        if session_id:
            self.connect_to_session(
                browser_name=browser_name,
                platform=platform,
                version=version,
                javascript_enabled=javascript_enabled
            )
        else:
            self.start_session(
                browser_name=browser_name,
                platform=platform,
                version=version,
                javascript_enabled=javascript_enabled
            )
            
    def connect_to_session(self, browser_name, platform, version, javascript_enabled):
        response =  self.execute('GET_SESSION', {
            'desiredCapabilities': {
                'browserName': browser_name,
                'platform': platform or 'ANY',
                'version': version or '',
                'javascriptEnabled': javascript_enabled
            },
            'sessionId': self.session_id
        })
        self.session_id = response['sessionId']
        self.capabilities = response['value']