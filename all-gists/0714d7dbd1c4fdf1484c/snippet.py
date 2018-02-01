# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, url_for, session, abort, current_app, json


app = Flask(__name__)
# This is the very unsecret key from the Flask-docs
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def index():
    return "Hello, world!", 200

# Url routing
@app.route('/myresource/<resource_id>')
def myresource(resource_id):
    return "This is myresource: %s. Trailing slashes are disabled on all resources." % resource_id, 200

@app.route('/myresource/<resource_id>/')
def myresource2(resource_id):
    return "This is myresource2: %s. Trailing slashes are enabled on all resources." % resource_id, 200


# POST echo form
@app.route('/post', methods=['GET', 'POST'])
def post_echo():
    if request.method == 'GET':
        return """
        <form action="" method="post">
            <p><input type=text name=mystring>
            <p><input type=submit value=Echo>
        </form>
        """
    if request.method == 'POST':
        return json.dumps(request.form)


# 301 redirect
@app.route('/redirect_me')
def redirect_page():
    print "url_for('redirect_target')", url_for('redirect_target')
    return redirect(url_for('redirect_target'))

@app.route('/redirect_target')
def redirect_target():
    return "At redirect target!", 200


# Cookie-setting page
@app.route('/set_cookie', methods=['GET', 'POST'])
def set_cookie():
    if request.method == 'GET':
        return """
        <form action="" method="post">
            <p>foo: <input type=text name=foo>
            <p>bar: <input type=text name=bar>
            <p><input type=submit value=SetCookie>
        </form>
        """
    session['foo'] = request.form['foo']
    response = current_app.make_response("Set cookies successfully. Now visit /read_cookie")
    response.set_cookie('bar', value=request.form['bar'])
    return response

@app.route('/read_cookie')
def read_cookie():
    found = ""
    try:
        found += "Found 'foo' %s in session. " % session['foo']
    except:
        found += "Couldn't find 'foo' in session."

    try:
        found += "Found 'bar': %s in cookies." % request.cookies['bar']
    except:
        found += "Couldn't find 'bar' in cookies."

    if found:
        return found
    else:
        return "Couldn't find cookies 'session' or 'baz'", 200

#a 400/401/403/404
@app.route('/abort/<int:abort_code>')
def myabort(abort_code):
    allowed_codes = [400, 401, 403, 404, 500]
    if abort_code in allowed_codes:
        abort(abort_code)
    else:
        return "Illegal abort code. Try one of %s" % str(allowed_codes)

#and an application/json content-type page
@app.route('/json')
def myjson():
    return json.jsonify(
        foo='bar',
        baz=123)
