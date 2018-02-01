"""
dot directive (require graphviz)
"""

from docutils import nodes
from docutils.parsers.rst import directives, Directive

import subprocess as sp

nthUnnamed = 0
class Dot(Directive):
    required_arguments = 0
    optional_arguments = 1
    has_content = True
    final_argument_whitespace = True

    '''dot image generator'''
    def run(self):
        self.assert_has_content()
        global nthUnnamed
        try:
            filename = self.arguments[0]
        except:
            filename = ('dot%d.png' % nthUnnamed)
            nthUnnamed += 1
        content = '\n'.join(self.content)
        filetype = filename[filename.rfind('.')+1:]
        args = ['dot', '-o'+filename, '-T'+filetype]
        dot = sp.Popen(args, 0, None, sp.PIPE)
        dot.stdin.write( content )
        dot.stdin.close()
        ret = dot.wait()
        if ret:
            return [nodes.error('some error occured')]
        else:
            return [nodes.raw('', '<img src="%s" alt="%s"/>'%(filename, filename), format='html')]
