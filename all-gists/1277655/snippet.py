import simplejson
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import flaskext.couchdb


app = Flask(__name__)

"""
CouchDB permanent view
"""
docs_by_author = ViewDefinition('docs', 'byauthor', 
                                'function(doc) { emit(doc.author, doc);}')

"""
Retrieve docs
"""
@app.route("/<author_id>/docs")
def docs(author_id):
    docs = []
    for row in docs_by_author(g.couch)[author_id]:
        docs.append(row.value)
    return simplejson.dumps(docs)

"""
Add doc
"""
@app.route("/<author_id>/add", methods=['POST'])
def add_doc(author_id):
    try:
        # Build doc with posted values
        doc = { 'author': author_id }
        doc.update(request.form)
        # Insert into database
        g.couch.save(doc)
        state = True
    except Exception, e:
        state = False
    return simplejson.dumps({'ok': state})


"""
Flask main
"""
if __name__ == "__main__":
    app.config.update(
        DEBUG = True,
        COUCHDB_SERVER = 'http://localhost:5984/',
        COUCHDB_DATABASE = 'docsdemo'
    )
    manager = flaskext.couchdb.CouchDBManager()
    manager.setup(app)
    manager.add_viewdef(docs_by_author)  # Install the view
    manager.sync(app)
    app.run(host='0.0.0.0', port=5000)
