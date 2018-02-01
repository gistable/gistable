import string
import sys
import logging
import json

from flask import Flask
from flask import Response, request

logger = logging.getLogger(__name__)
logger.info("Stackdriver webhook-sample starting up on %s" % (string.replace(sys.version, '\n', ' ')))

app = Flask("webhook-sample")


@app.route('/simple', methods=['POST'])
def simple_handler():
    """ Handle a webhook post with no authentication method """
    json_data = json.loads(request.data)
    logger.info(json.dumps(json_data, indent=4))
    return Response("OK")


@app.route('/basic-auth', methods=['POST'])
def basic_auth_handler():
    """ Handle a webhook post with basic HTTP authentication """
    auth = request.authorization

    if not auth or not _check_basic_auth(auth.username, auth.password):
        error_msg = '401 Could not verify your access level for that URL. You have to login with proper credentials'
        logger.error(error_msg)
        # A correct 401 authentication challenge with the realm specified is required
        return Response(error_msg, 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    else:
        logger.info("auth success")
        json_data = json.loads(request.data)
        logger.info(json.dumps(json_data, indent=4))
        return Response("OK")


@app.route('/token-auth', methods=['POST'])
def token_auth_handler():
    """ Handle a webhook post with an associated authentication token """
    auth_token = request.args.get('auth_token')

    if not auth_token or not _check_token_auth(auth_token):
        error_msg = '403 Please pass the correct authentication token'
        logger.error(error_msg)
        return Response(error_msg, 403)
    else:
        logger.info("auth success")
        json_data = json.loads(request.data)
        logger.info(json.dumps(json_data, indent=4))
        return Response("OK")


def _check_basic_auth(username, password):
    """This function is called to check if a username / password combination is valid. """
    return username == 'admin' and password == 'secret'


def _check_token_auth(auth_token):
    """This function is called to check if a submitted token argument matches the expected token """
    return auth_token == "9bdd7020-5395-11e3-8f96-0800200c9a66"
