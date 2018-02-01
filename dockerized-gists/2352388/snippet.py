# http://flask.pocoo.org/mailinglist/archive/2012/4/10/serving-static-file-from-a-separate-domain-in-production/

from flask import Flask, url_for

# Uncomment to set server name.
# SERVER_NAME = 'mianos.com'

app = Flask(__name__, static_folder=None)
app.config.from_object(__name__)
app.add_url_rule('/<path:filename>', endpoint='static',
                 view_func=app.send_static_file, subdomain='static')

@app.route('/')
def index():
    return url_for('static', filename='style.css')


if __name__ == '__main__':
    app.run(debug=True)
