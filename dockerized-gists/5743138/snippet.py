#http://stackoverflow.com/questions/5870188/does-flask-support-regular-expressions-in-its-url-routing
#Even though Armin beat me to the punch with an accepted answer I thought I'd show an abbreviated example of how I implemented a regex matcher in Flask just in case anyone wants a working example of how this could be done.

from flask import Flask
from werkzeug.routing import BaseConverter

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

@app.route('/<regex("[abcABC0-9]{4,6}"):uid>-<slug>/')
def example(uid, slug):
    return "uid: %s, slug: %s" % (uid, slug)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

#this URL should return with 200: http://localhost:5000/abc0-foo/
#this URL should will return with 404: http://localhost:5000/abcd-foo/