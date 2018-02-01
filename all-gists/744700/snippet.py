from pymongo import Connection
from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for
from .util import normalize_url

app = Flask(__name__)

conn = Connection('localhost')
db = conn.test
bookmarkr = db.bookmarkr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import', methods=['GET', 'POST'])
def import_bookmark():
    if request.method == 'GET':
        return render_template('import.html')

    if request.files and request.files['file']:
        src = request.files['file'].read()
        soup = BeautifulSoup(src)
        items = [{'href': normalize_url(a.get('href'), True),
            'title': a.string, 'tags': a.get('tags').split(',')}
            for a in soup.findAll('a')]
        bookmarkr.insert(items)
    return redirect(url_for('list'))

@app.route('/list')
def list():
    return render_template('list.html', links=bookmarkr.find().limit(50))
