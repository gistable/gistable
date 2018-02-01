# assuming static/js/border.js exists

from flask import Flask, render_template_string
import jinja2
import os

app = Flask(__name__)
app.secret_key = 'WOO'

def include_file(name):
    directory = app.static_folder
    desired_file = os.path.join(directory, name)
    if not os.path.exists(desired_file):
        raise IOError
    with open(desired_file) as f:
        return jinja2.Markup(f.read().decode('utf-8'))

app.jinja_env.globals["include_file"] = include_file

@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template_string("{{ include_file('border.js') }}")


if __name__ == '__main__':
    app.run(debug=True, port=5002)
