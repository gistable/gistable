import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = u'Example_Toolbox'
        self.alias = ''
        self.tools = [FirstTool, SecondTool, ThirdTool]


class FirstTool(object):

    def __init__(self):
        self.label = u'First Tool'
        self.description = u''
        self.canRunInBackground = False
        self.category = "Import"

    def getParameterInfo(self):
        return

    def execute(self, parameters, messages):
        pass

class SecondTool(object):

    def __init__(self):
        self.label = u'Second Tool'
        self.description = u''
        self.canRunInBackground = False
        self.category = "Export"

    def getParameterInfo(self):
        return

    def execute(self, parameters, messages):
        pass

class ThirdTool(object):

    def __init__(self):
        self.label = u'Third Tool'
        self.description = u''
        self.canRunInBackground = False
        self.category = "Export"

    def getParameterInfo(self):
        return

    def execute(self, parameters, messages):
        pass
