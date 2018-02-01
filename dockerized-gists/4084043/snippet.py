import requests
import json

class ValidationException(Exception):
    pass

class Element34(object):
    def __init__(self, driver):
        self.driver = driver
        
    def open(self):
        self.driver.get('http://element34.ca')
        return self
    
    def wait_until_loaded(self):
        return self
        
    def validate(self):
        post_data = {
            "fragment": self.driver.page_source,
            "output": "json",
            "doctype": "XHTML 1.0 Transitional"
        }
        r = requests.post('http://validator.w3.org/check', data=post_data)

        j = json.loads(r.text)
        
        validation_errors = []
        if r.headers['x-w3c-validator-errors'] != 0:
            for m in j['messages']:
                if m['type'] == 'error':
                    validation_errors.append(m)
        
        validation_warnings = []
        if r.headers['x-w3c-validator-warnings'] != 0:
            for m in j['messages']:
                if m['type'] == 'info':
                    validation_warnings.append(m)
        
        if len(validation_errors) != 0 or len(validation_warnings) != 0:
            raise ValidationException('There were %d validation errors and %d validation warnings' % (len(validation_errors), len(validation_warnings)))
