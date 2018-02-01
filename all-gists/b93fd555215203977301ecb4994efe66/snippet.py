"""Reactive expressions for Dash!

Dash[1] is an interesting project build reactive web applications in Python.
While the ideas are exciting, the syntax for specifying custom code is way
too complicated that it should be.

Here is a sample code to display sum of two input values.

@app.callback(
    [Input(component_id='x', component_property='value')]
    [Input(component_id='y', component_property='value')]
    Output(component_id='output', component_property='children'),
)
def add(x, y):
    return int(x) + int(y)

Wouldn't it is nice that like an expression?

app['output'].children = add(app['x'].value, app['y'].value)

This is an proof of concept implementation to demonstrate that it is possible!

[1]: https://plot.ly/dash/

"""
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

class ReactiveDash(dash.Dash):
    def __getitem__(self, id):
        return ReactiveElement(self, id)

    def reactive(self, func):
        return ReactiveFunction(self, func)

class ReactiveNode:
    def get_inputs(self):
        return []

class ReactiveElement(ReactiveNode):
    def __init__(self, app, id):
        self._app = app
        self._id = id

    def __getattr__(self, property_name):
        return ReactiveProperty(self._app, self, property_name)

    def __setattr__(self, property_name, value):
        if property_name.startswith("_"):
            return super().__setattr__(property_name, value)

        # print("__setattr__", property_name)

        if not isinstance(value, ReactiveNode):
            raise Exception("Expected a reactive expression")
        output = Output(component_id=self._id, component_property=property_name)
        raw_inputs = list(value.get_inputs())
        inputs = [Input(component_id=x.element._id, component_property=x.property_name)
                    for x in raw_inputs]
        input_keys = [x.get_key() for x in raw_inputs]

        # print("value", value)
        # print("inputs", raw_inputs)
        # print("input_keys", input_keys)

        @self._app.callback(output=output, inputs=inputs)
        def callback_func(*args):
            # print("callback", args)
            env = dict(zip(input_keys, args))
            return value.evaluate(env)

    def __repr__(self):
        return "<#{}>".format(self._id)

class ReactiveProperty(ReactiveNode):
    def __init__(self, app, element, property_name):
        self.app = app
        self.element = element
        self.property_name = property_name

    def get_key(self):
        return (self.element._id, self.property_name)

    def evaluate(self, env):
        return env[self.element._id, self.property_name]

    def get_inputs(self):
        return [self]

    def __repr__(self):
        return "{}.{}".format(self.element, self.property_name)

class ReactiveFunction(ReactiveNode):
    def __init__(self, app, func):
        self.app = app
        self.func = func

    def __call__(self, *args):
        return ReactiveFunctionCall(self.app, self.func, *args)

    def __repr__(self):
        return "<{}()>".format(self.func.__name__)

class ReactiveFunctionCall(ReactiveNode):
    def __init__(self, app, func, *args):
        self.app = app
        self.func = func
        self.args = args

    def get_inputs(self):
        for a in self.args:
            if isinstance(a, ReactiveNode):
                yield from a.get_inputs()

    def evaluate(self, env):
        args = [a.evaluate(env) for a in self.args]
        return self.func(*args)

    def __repr__(self):
        args = ", ".join(repr(a) for a in self.args)
        return "{}({})".format(self.func.__name__, args)


def make_sample_app():
    app = ReactiveDash()
    app.layout = html.Div([
        html.Div(
            [html.Label("X", htmlFor='x'),
             dcc.Input(id='x', value='1', type="text")]),
        html.Div(
            [html.Label("Y", htmlFor='y'),
             dcc.Input(id='y', value='2', type="text")]),
        html.Div(id='output')
    ])

    @app.reactive
    def add(x, y):
        return int(x)+int(y)

    app['output'].children = add(app['x'].value, app['y'].value)

    return app

def main():
    app = make_sample_app()
    app.run_server()

if __name__ == "__main__":
    main()
