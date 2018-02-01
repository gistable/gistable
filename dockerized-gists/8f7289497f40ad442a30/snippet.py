from IPython.core.magic import Magics, magics_class, line_magic
import asyncio


@magics_class
class AsyncMagics(Magics):
    @line_magic
    def await(self, line):
        return asyncio.get_event_loop().run_until_complete(eval(line, self.shell.user_global_ns, self.shell.user_ns))


def load_ipython_extension(ipython):
    ipython.register_magics(AsyncMagics)