
from itsdangerous import JSONWebSignatureSerializer, BadSignature, SignatureExpired
import calendar
import datetime

class TimedJSONWebSignatureSerializer(JSONWebSignatureSerializer):

    EXPIRES_IN_AN_HOUR = 3600

    def __init__(self, secret_key, salt=None, serializer=None, signer=None, signer_kwargs=None, algorithm_name=None, expires_in=None):
        super(TimedJSONWebSignatureSerializer, self).__init__(secret_key, salt, serializer, signer, signer_kwargs,
            algorithm_name)
        if not expires_in:
            expires_in = self.EXPIRES_IN_AN_HOUR
        self.expires_in = expires_in

    def loads(self, s, salt=None, return_header=False):
        payload = super(TimedJSONWebSignatureSerializer, self).loads(s, salt, return_header)

        if not 'exp' in payload:
            raise BadSignature("Missing ['exp'] expiry date", payload=payload)

        if not isinstance(payload['exp'], int) and payload['exp'] > 0:
            raise BadSignature("['exp'] expiry date is not and IntDate", payload=payload)

        if payload['exp'] < self.now():
            raise SignatureExpired(
                'Signature expired',
                payload=payload)

        return super(TimedJSONWebSignatureSerializer, self).loads(s, salt, return_header)

    def dumps(self, obj, salt=None, header_fields=None):
        iat = self.now()
        exp = iat + self.expires_in
        obj['iat'] = iat
        obj['exp'] = exp
        return super(TimedJSONWebSignatureSerializer, self).dumps(obj, salt=salt, header_fields=header_fields)

    def now(self):
        return calendar.timegm(datetime.datetime.utcnow().utctimetuple())
  

import mock
from hamcrest import *


class TimedJSONWebSignatureSerializerTest(unittest.TestCase): 
 
    def setUp(self): 
        # Use the original implementation to create 'invalid' tokens 
        self.invalid_token_empty = JSONWebSignatureSerializer("secret").dumps({}) 
        self.invalid_token_wrong_type = JSONWebSignatureSerializer("secret").dumps({'exp':'geloet'}) 
 
    def test_token_contains_issue_date_and_expiry_time(self): 
        t = TimedJSONWebSignatureSerializer("secret") 
        result = t.dumps({'es': 'geht'}) 
        assert_that(t.loads(result), has_items('exp', 'iat')) 
 
    def test_token_expires_at_given_expiry_time(self): 
        s = TimedJSONWebSignatureSerializer("secret") 
        an_hour_ago = calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - 3601 
        s.now = mock.MagicMock(return_value=an_hour_ago) 
        result = s.dumps({'foo':'bar'}) 
        with self.assertRaises(SignatureExpired): 
            TimedJSONWebSignatureSerializer('secret').loads(result) 
 
    def test_token_is_invalid_if_expiry_time_is_missing(self): 
        t = TimedJSONWebSignatureSerializer("secret") 
        with self.assertRaises(BadSignature): 
            t.loads(self.invalid_token_empty) 
 
    def test_token_is_invalid_if_expiry_time_is_of_wrong_type(self): 
        t = TimedJSONWebSignatureSerializer("secret") 
        with self.assertRaises(BadSignature): 
            t.loads(self.invalid_token_wrong_type) 
 
    def test_creating_a_token_adds_the_expiry_date(self): 
        EXPIRES_IN_TWO_HOURS = 7200 
        t = TimedJSONWebSignatureSerializer("secret", expires_in=EXPIRES_IN_TWO_HOURS) 
        result = t.loads(t.dumps({'foo': 'bar'})) 
        assert_that(result['exp'] - result['iat'], is_(EXPIRES_IN_TWO_HOURS)) 