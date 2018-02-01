"""
Test if a request is XHR.
"""

import argparse
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route('/')
def home():
    """Home page."""
    return make_response("""
    <!doctype html>
    <html>
    <head>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <script type="text/javascript">
          $(function() {
            $.get('/test').then(function(data) {
                console.log(data)
            })
          })
        </script>
    </head>
    <body>
        <h1>Home page</h1>
    </body>
    </html>
    """)


@app.route('/test')
def test():
    if request.is_xhr:
        return jsonify({'hello': 'world'})
    return "Hello, world."


def parse_arguments():
    """Parse any arguments that may be passed to the file."""
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', default=5000, type=int,
                        help="An integer for the port you want to use.")
    return parser.parse_args()


def main():
    environment = parse_arguments()
    app.run(debug=True, port=environment.port)


if __name__ == '__main__':
    main()