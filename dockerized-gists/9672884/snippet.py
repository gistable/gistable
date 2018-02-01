from flask import Flask, request
import hmac
import urllib
import json
app = Flask(__name__)

app.secret_key = 'THIS IS A SECRET KEY (JUST KIDDING)'


def get_auth_code(payload):
    return hmac.new(app.config['SECRET_KEY'], json.dumps(payload)).hexdigest()


def create_payload(email):
    payload = {
        "email": str(email)
    }
    return payload


def get_url_keys(payload):
    url_keys = {
        'auth_code': get_auth_code(payload)
    }
    url_keys.update(payload)
    return urllib.urlencode(url_keys)


class PassResetError(Exception):
    pass


def check_passreset(payload, auth_code):
    new_code = get_auth_code(payload)
    if new_code != auth_code:
        raise PassResetError("Invalid password reset request")


@app.route("/", methods=['GET', 'POST'])
def passreset():
    if request.method == 'GET':
        return """
            <p>Forget your password? Enter your email below to reset it.</p>
            <form method='POST'>
                <input type='text' name='reset_email' />
                <button type='submit'>Reset your password</button>
            </form>"""
    else:
        payload = create_payload(request.form['reset_email'])
        url = "/passreset?%s" % get_url_keys(payload)
        return """
            <p>
                This should really be in an email.
                Use the link below to reset your password
            </p>
            <a href="%(url)s">
                %(url)s
            </a>""" % {"url": url}


@app.route("/passreset")
def newpass():
    # Need to check for both methods
    try:
        payload = {
            "email": str(request.args['email']),
        }
        auth_code = str(request.args['auth_code'])
        check_passreset(payload, auth_code)
    except KeyError:
        # Check for missing form elements
        return "Invalid password reset request (form elements)"
    except PassResetError, e:
        return str(e)
    # We're in the clear, give them the password reset form
    return "Good to go! Here's where I'd render a new password form."


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')