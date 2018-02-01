@app.get(r'^/$')
def index(http):
    return 'homepage'

@app.get(r'^/phail$')
def phailure(http):
    raise Exception("I have no idea what I'm doing")

@app.handle_500
def on_failure(http):
    return 'woops! cute message here'
