from flask import Flask

app = Flask("proxapp")


@app.route('/')
def hello_world():
    return 'Hello World!'


# since we're using threads, shouldn't we be able to pause execution of one?
@app.route('/slow')
def slow():
    import time
    time.sleep(10)
    return 'zzz'

with open('./log', 'a+') as log:
    try:
        app.run(threaded=True)
        log.write("done adding wsgi app\n")
    except Exception, e:
        log.write(repr(e))
