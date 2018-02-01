from burp import (IBurpExtender, IBurpExtenderCallbacks, ISessionHandlingAction, IHttpListener)
import re

class BurpExtender(IBurpExtender, ISessionHandlingAction, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Session CSRF Token Handling")
        self.callbacks.registerSessionHandlingAction(self)
        self.callbacks.registerHttpListener(self)
        self.out = callbacks.getStdout()
        # CONFIG: find token in tools defined by this bitmask, constants defined in IBurpExtenderCallback
        self.findTools = 0xffffffff
        # CONFIG: this RE matches the CSRF token
        self.reFindToken = re.compile("^<script>var csrfToken=\"(.*?)\"", re.MULTILINE)
        # CONFIG: Replacement RE with prefix and suffix capture groups
        self.reReplaceToken = re.compile("(CSRFToken=).*?(&)")
        self.token = None

    def log(self, msg):
        self.out.write(msg + "\n")

    ### IHttpListener ###
    def processHttpMessage(self, tool, messageIsRequest, message):
        if tool & self.findTools and not messageIsRequest:
            response = self.helpers.bytesToString(message.getResponse())
            match = self.reFindToken.search(response)
            if match and self.token != match.group(1):
                self.token = match.group(1)
                self.log("New CSRF Token: " + self.token)

    ### ISessionHandlingAction ###
    def getActionName(self):
        return "Update CSRF Token"
    
    def performAction(self, currentRequest, macroItems):
        request = self.helpers.bytesToString(currentRequest.getRequest())
        result = self.reReplaceToken.sub("\\g<1>" + self.token + "\\g<2>", request)
        currentRequest.setRequest(result)