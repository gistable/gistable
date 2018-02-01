#!/usr/bin/env python
import Globals

from Products.ZenUtils.ZenScriptBase import ZenScriptBase

class MyTool(ZenScriptBase):
    def buildOptions(self):
        super(MyTool, self).buildOptions()

        self.parser.add_option(
            '-x', dest='myoption',
            help='My option.')

    def run(self):
        print "%s - %s" % (self.dmd, self.options.myoption)

if __name__ == '__main__':
    tool = MyTool(connect=True)
    tool.run()