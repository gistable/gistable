# (c) Thomas Kluyver, 2016
# Use it under the MIT license

# This is fairly experimental. Use at your own risk.

import ast
from ast import Call, Attribute, Name, Load
import asyncio as asyncio_mod
#import astpp
from IPython.utils.text import indent

class RewriteAwait(ast.NodeTransformer):
    def visit_Await(self, node):
        self.generic_visit(node)
        new = Call(func=Attribute(
            value=Call(func=Attribute(value=Name(id='_asyncio', ctx=Load()),
            attr='get_event_loop', ctx=Load()), args=[], keywords=[]),
        attr='run_until_complete', ctx=Load()), args=[node.value], keywords=[])
        return ast.copy_location(new, node)
    
    def visit_AsyncFunctionDef(self, node):
        # Don't transform awaits inside an 'async def' function
        return node
    
    def visit_Return(self, node):
        raise SyntaxError("Return outside function definition")
    

def load_ipython_extension(ip):
    def asyncio(line, cell):
        code_in_func = "async def __f():\n" + indent(cell)
        mod = ast.parse(code_in_func)
        body = mod.body[0].body
        new_mod = ast.Module([RewriteAwait().visit(n) for n in body])
        ast.fix_missing_locations(new_mod)
        #print(astpp.dump(new_mod))
        co = compile(new_mod, filename="<asyncio_magic>", mode="exec")
        ip.user_global_ns['_asyncio'] = asyncio_mod
        ip.ex(co)

    ip.register_magic_function(asyncio, 'cell')
