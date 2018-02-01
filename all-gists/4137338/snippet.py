from flask import *

app = Flask(__name__)

@app.route('/event.gif')
def log_event():
    event = request.args
    model = event.get('_id', '')
    # pull model from meta
    # validate model
    return Response(status=204)

if __name__ == '__main__':
    app.run()