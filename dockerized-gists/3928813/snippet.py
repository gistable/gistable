from flask import Flask, Blueprint, request

## blueprint ##################################################################

bp = Blueprint('category_functionality', __name__)

@bp.route('/')
def index(category):
    return "this is the index page for %r" % category

@bp.route('/list')
def list(category):
    return "return a list of %r" % category

## app ########################################################################

app = Flask(__name__)
app.config['DEBUG'] = True
app.register_blueprint(bp, url_prefix="/<path:category>")

@app.route("/")
def index():
    return "index"

if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True)
