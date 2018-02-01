from flask import Flask, request, redirect, url_for, make_response, abort
from werkzeug import secure_filename
from pymongo import Connection
from pymongo.objectid import ObjectId
from gridfs import GridFS
from gridfs.errors import NoFile

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
DB = Connection().gridfs_server_test
FS = GridFS(DB)

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            oid = FS.put(file, content_type=file.content_type, filename=filename)
            return redirect(url_for('serve_gridfs_file', oid=str(oid)))            
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Upload new file</title>
    </head>
    <body>
    <h1>Upload new file</h1>
    <form action="" method="post" enctype="multipart/form-data">
    <p><input type="file" name="file"></p>
    <p><input type="submit" value="Upload"></p>
    </form>
    <a href="%s">All files</a>
    </body>
    </html>
    ''' % url_for('list_gridfs_files')

@app.route('/files')
def list_gridfs_files():
    files = [FS.get_last_version(file) for file in FS.list()]
    file_list = "\n".join(['<li><a href="%s">%s</a></li>' % \
                            (url_for('serve_gridfs_file', oid=str(file._id)), file.name) \
                            for file in files])
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Files</title>
    </head>
    <body>
    <h1>Files</h1>
    <ul>
    %s
    </ul>
    <a href="%s">Upload new file</a>
    </body>
    </html>
    ''' % (file_list, url_for('upload_file'))

@app.route('/files/<oid>')
def serve_gridfs_file(oid):
    try:
        file = FS.get(ObjectId(oid))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)