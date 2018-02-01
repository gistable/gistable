import execjs
import os
here = os.path.dirname(__file__)
node_modules = os.path.abspath(os.path.join(here, './node_modules'))

class Babel:
    def __init__(self, *module_paths):
        """Constructor

        :param module_paths: Paths to node_modules
        """
        self.paths = module_paths
        # This is used to let execjs know where the
        # modules are
        self.module_append_string = '\n'.join(
            'module.paths.push("%s")\n' % p for p in self.paths
        )
        command_string = 'var babel = require("babel-core")'
        self.babel = execjs.compile(self.module_append_string + command_string)

    def transpile(self, code, options=None):
        """Takes code and runs it through babel.js

        if ``options`` is not provided it'll default to:

        .. code-block:: python

            {'ast': false, 'presets': ['react', 'es2015']}
        """
        if options is None:
            options = {
                'ast': False,
                'presets': ['react', 'es2015'],
            }

        transpiled_code = self.babel.call(
            'babel.transform', code, options
        )['code']

        return transpiled_code

class React:
    def __init__(self, babel):
        """Constructor

        :param babel: Instance of ``babel``.
        """
        self.babel = babel
        self.codes = []

    def add_code(self, code):
        """Registers some code to be included

        This registers a class to be included in the rendering context.
        """
        self.codes.append(code)

    def render_string(self, code):
        """Renders a string of JSX

        This will take a JSX string and render it to HTML
        """
        classes = '\n'.join(
            '{0};'.format(code) for code in self.codes
        )

        # we don't use `es2015` preset here because it
        # forces `use strict`
        element_options = {'ast': False, 'presets': ['react']}
        element = self.babel.transpile(code, element_options)
        es6_code = """
import ReactDOMServer from "react-dom/server";
{0}
function __render() {{
    var element = {1}
    return ReactDOMServer.renderToString(element);
}};""".format(classes, element);
        transpiled = self.babel.transpile(es6_code)
        final_code = self.babel.module_append_string + transpiled
        compiled = execjs.compile(final_code)
        result = compiled.call('__render')
        return result


babel = Babel(node_modules)
react = React(babel)
original_source = """
import React from "react";

class HelloWorld extends React.Component {
    render() {
        return <p>Hello, world!</p>;
    }
}
"""
react.add_code(original_source)
print(react.render_string("<HelloWorld />"))
