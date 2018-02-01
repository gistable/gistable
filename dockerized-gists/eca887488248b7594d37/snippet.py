import re
import tokenize

import astroid



def _build_assign(value):
    return astroid.parse('_ = {}'.format(value)).body[0]

def inject_imports(module):
    hint = re.compile('# type: \((.*?)\)')
    with module.stream() as stream:
        for token in tokenize.generate_tokens(lambda: stream.readline().decode()):
           if token.type != tokenize.COMMENT:
              continue
           found = hint.search(token.string)
           matches = found.group(1).split(",")
           for name in matches:  
               module.body.append(_build_assign(name))
    return module



astroid.MANAGER.register_transform(astroid.Module, inject_imports)

def register(linter):
    pass