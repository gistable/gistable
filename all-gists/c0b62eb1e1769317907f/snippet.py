# Render the template for the upload form:

@app.route("/upload")
def upload():
    uploadUri = blobstore.create_upload_url('/submit', gs_bucket_name=BUCKET_NAME)
    return render_template('upload.html', uploadUri=uploadUri)

# Place your uploadUri in the form path (html):

'''<form action="{{ uploadUri }}" method="POST" enctype="multipart/form-data">'''


# Here is the function to handle the upload of the image (I return the blob_key for practical reasons, replace it with your template):

@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        f = request.files['file']
        header = f.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        return blob_key

# Now say you serve your images with a path like this:
# /img/imagefilename
# Then your image serving function is :

@app.route("/img/<bkey>")
def img(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

# Finally, anywhere you need to display an image in a template, you simply put the code:
'''<img src="/img/{{ bkey }} />'''