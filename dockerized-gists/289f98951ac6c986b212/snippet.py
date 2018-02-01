from bottle import Bottle, run, request, response, HTTPResponse

APP1 = Bottle()

@APP1.hook('before_request')
def before_request():  
    print "APP 1 - Before Request {}".format(request.url)

@APP1.hook('after_request')
def after_request():  
    print "APP 1 - After Request {} - status code: {}".format(request.url, response.status_code)

@APP1.route('/error')
def error():  
    raise HTTPResponse(status=400)

if __name__ == "__main__":  
    run(APP1, host='localhost', port=8080) 