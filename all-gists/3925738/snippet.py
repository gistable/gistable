from flask import Flask, render_template_string, request

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask(__name__)
app.config['DEBUG'] = True

@app.route("/")
def index():
    template = """
    <# this is a jinja2 comment #>
    <% block stuff %>
        <h1>Jinja2</h1>
        <% for i in range(5) %>
            <p>Hello %% name %%!</p>
        <% endfor %>

        <h1>Mustache</h1>
        <p>{{something}}</p>
        {{#items}}
          {{#first}}
            <li><strong>{{name}}</strong></li>
          {{/first}}
          {{#link}}
            <li><a href="{{url}}">{{name}}</a></li>
          {{/link}}
        {{/items}}
    <% endblock %>
    """
    return render_template_string(template, name=request.values.get('name', 'world'))


if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True)