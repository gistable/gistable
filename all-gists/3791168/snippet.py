"""
    Demo of json_required decorator for API input validation/error handling
"""

import inspect
import functools
import json
from traceback import format_exception
from flask import jsonify, request
import sys
from flask.exceptions import JSONBadRequest

from flask import Flask
import re

app = Flask(__name__)

def api_error_response(code=404, message="Requested resource was not found", errors=list()):
    """
        Convenience function for returning a JSON response that includes
        appropriate error messages and code.
    """

    response = jsonify(dict(code=code, message=message, errors=errors, success=False))
    response.status_code = code
    return response

def bad_json_error_response():
    """
        Convenience function for returning an error message related to
        malformed/missing JSON data.
    """

    return api_error_response(code=400,
        message="There was a problem parsing the supplied JSON data.  Please send valid JSON.")


def json_required(func=None, required_fields={}, validations=[]):
    """
        Decorator used to validate JSON input to an API request
    """
    if func is None:
        return functools.partial(json_required, required_fields=required_fields, validations=validations)
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):

        try:
            #If no JSON was supplied (or it didn't parse correctly)
            try:
                if request.json is None:
                    return bad_json_error_response()
            except JSONBadRequest:
                return bad_json_error_response()

            #Check for specific fields
            errors = []

            def check_required_fields(data, fields):
                for field, requirements in fields.iteritems():
                    nested_fields = type(requirements) == dict
                    if data.get(field) in (None, ''):
                        if nested_fields:
                            error_msg = requirements.get('message')
                        else:
                            error_msg = requirements
                        errors.append({'field': field, 'message': error_msg})
                    elif nested_fields:
                        check_required_fields(data[field], requirements.get('fields', {}))

            check_required_fields(request.json, required_fields)

            for validation_field, validation_message, validation_func in validations:
                func_args = inspect.getargspec(validation_func).args
                func_params = []
                for arg in func_args:
                    func_params.append(request.json.get(arg))

                if not validation_func(*func_params):
                    errors.append({'field': validation_field, 'message': validation_message})

            if errors:
                return api_error_response(code=422, message="JSON Validation Failed", errors=errors)

        except Exception:
            #For internal use, nice to have the traceback in the API response for debugging
            #Probably don't want to include for public APIs
            etype, value, tb = sys.exc_info()
            error_info = ''.join(format_exception(etype, value, tb))
            return api_error_response(code=500, message="Internal Error validating API input", errors=[{'message':error_info}])

        return func(*args, **kwargs)

    return decorated_function

EMAIL_REGEX = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?")

def verify_account_available(email):
    """
        Check to see if this email is already registered
    """

    #Run a query, use an ORM, use Twilio to call someone and ask them :-)
    return True

def valid_date_of_birth(date_of_birth):
    """
        Does the supplied date string meet our criteria for a date of birth
    """

    #Do whatever you need to do...
    return True

@app.route("/do/something", methods=['POST'])
@json_required(
    required_fields={
        'first_name':"Please provide your first name.",
        'last_name':"Please provide your last name.",
        'email':'Please specify a valid email address',
        'date_of_birth':'Please provide your date of birth'
    },
    validations=[
        ('email', 'Please provide a valid email address', lambda email: email is not None and EMAIL_REGEX.match(email)),
        ('email', "This email is already in use.  Please try a different email address.", verify_account_available),
        ('date_of_birth', 'Please provide a valid date of birth', valid_date_of_birth)
    ]
)
def do_something_useful():
    #Confidently use the data in request.json...
    return jsonify(dict(status='OK'))


if __name__ == "__main__":

    with app.test_client() as client:
        response = client.post(
            '/do/something',
            data=json.dumps({ "first_name": "Brian",
                              "last_name": "Corbin",
                              "email": "corbinbs@example.com",
                              "date_of_birth": "01/01/1970" }),
            follow_redirects=True,
            content_type='application/json')

        response_dict = json.loads(response.data)
        assert response_dict['status'] == 'OK'

        response = client.post(
            '/do/something',
            data=json.dumps({ "last_name": "Corbin",
                              "email": "corbinbs@example.com",
                              "date_of_birth": "01/01/1970" }),
            follow_redirects=True,
            content_type='application/json')

        response_dict = json.loads(response.data)
        assert response.status_code == 422
        assert response_dict['code'] == 422
        assert response_dict['message'] == "JSON Validation Failed"
        assert len(response_dict['errors']) == 1
        assert response_dict['errors'][0]['field'] == 'first_name'
        assert response_dict['errors'][0]['message'] == 'Please provide your first name.'
