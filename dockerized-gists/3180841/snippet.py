from flask import Flask, redirect, url_for, request

app = Flask(__name__)

is_maintenance_mode = True

# Always throw a 503 during maintenance: http://is.gd/DksGDm

@app.before_request
def check_for_maintenance():
    if is_maintenance_mode and request.path != url_for('maintenance'): 
        return redirect(url_for('maintenance'))
        # Or alternatively, dont redirect 
        # return 'Sorry, off for maintenance!', 503


@app.route('/')
def index():
    return 'Hello!'

@app.route('/maintenance')
def maintenance():
    return 'Sorry, off for maintenance!', 503

if __name__ == '__main__':
    app.run()
