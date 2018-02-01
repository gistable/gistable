from flask import Flask, request, Response, abort
from flask.ext.restful import Api, Resource,
from hashlib import sha256
import hmac, redis

CHARGIFY_SHARED_KEY= "XYZ789"
REDIS_HOST="ip_address"
REDIS_PORT="1234"
FLASK_HOST="ip_address"
FLASK_PORT="1234"

app = Flask(__name__)
api = Api(app)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)

class Customer_Signup(Resource):
    
    def parse_chargify_webhook(post_data):
        '''
        Converts Chargify webhook parameters to a python dictionary of nested dictionaries
        '''
        result = {}
        for k, v in post_data.iteritems():
            keys = [x.strip(']') for x in k.split('[')]
            cur = result
            for key in keys[:-1]:
                cur = cur.setdefault(key, {})
            cur[keys[-1]] = v
        return result

    def post(self):
        '''
        Recives a Chargify sends a webhook
        (https://docs.chargify.com/webhooks#signup-success-payload)
        '''
        # 1 Compare the Chargify webhook signature, if not then abort
        signature = request.headers.get('X-Chargify-Webhook-Signature-Hmac-Sha-256')
        if not hmac.compare_digest(signature, hmac.new(CHARGIFY_SHARED_KEY, request.get_data(), sha256).hexdigest()): abort(404)
        # Python 2.7.6 and lower, can use this less secure version: if not (signature == hmac.new(CHARGIFY_SHARED_KEY, request.get_data(), sha256).hexdigest()): abort(404)

        # 2. Check the webhook id has not been processed already 
        # 2.1 Get the webhook_id of this webhook
        webhook_data=parse_chargify_webhook(request.form)
        webhook_id=webhook_data["id"]

        # 2.1 If the key does not exisit in redis, set a new key
        if (r.get(webhook_id) == None):
            # key to expire after 330 seconds (chargify limit for resent webhooks)
            r.setex(webhook_id, 330, 'completed')
            # continue
            
        else: # this key exists and does not need to be processed again, so exit
            return Response(status=202)
        
        # 3 Get the customer_id from the webhook payload
        customer_id=webhook_data["payload"]["subscription"]["customer"]["id"]
        
        # 4. Call the main function to be executed (need to use celery for long running tasks)
        customer_signup_function(customer_id)
        
        # 5. Tell chargify we have processed this webhook correctly (within 10 seconds)
        return Response(status=202)

api.add_resource(Customer_Signup, '/api/customer_signup/')

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT)