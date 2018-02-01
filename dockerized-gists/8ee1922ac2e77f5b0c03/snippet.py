# coding: utf-8
import json
import stripe
import datetime

# Required for OAuth flow
from rauth import OAuth2Service

# Our secret key from stripe
STRIPE_SECRET_KEY = 'sk_test_xxxxxxxxxxxxx'
STRIPE_OAUTH_CLIENT_ID = 'ca_xxxxxxxxxxxxxxx'
NOW = datetime.datetime.now()

"""

The use of Stripe Connect to create a payment platform isn't as well documented as I'd like.  

Here's a bit of code that walks you through the whole process from the start - 

+ The OAuth flow
+ Creating a customer
+ Saving their credit card
+ Charging the customer
+ Creating a connect customer
+ Charging the connect customer
+ Updating the connect customer's credit card

+ Charging somebody via Connect without saving the customer

"""

# Set up your OAuth flow parameters
params = {'response_type': 'code', 'scope': 'admin'}
stripe_connect_service = OAuth2Service(
        name='stripe',
        client_id=STRIPE_OAUTH_CLIENT_ID,
        client_secret=STRIPE_SECRET_KEY,
        authorize_url='https://connect.stripe.com/oauth/authorize',
        access_token_url='https://connect.stripe.com/oauth/token',
        base_url='https://api.stripe.com/',
    )
    
# Build a URL to send them off to.  Redirect them to this URL
url = stripe_connect_service.get_authorize_url(**params)

# They return to your site from filling out a form on stripe and...
# There's a temporary code returned when they're redirected to your site.  
# In Django, you would grab it like this
code = request.GET.get('code', '')
  
# Tell stripe what you want
data = {
  'grant_type': 'authorization_code',
  'code': code
}

# Use your OAuth service to get a response
resp = stripe_connect_service.get_raw_access_token(method='POST', data=data)

# They returned JSON
stripe_payload = json.loads(resp.text)

# They return four parameters.  We only care about the 'access_token' right now, 
# but its important to store all of them.
connect_public_key = stripe_payload['stripe_publishable_key']
connect_access_token = stripe_payload['access_token']
connect_user_id = stripe_payload['stripe_user_id']
connect_refresh_token = stripe_payload['refresh_token']

# Now we make a card and a customer
my_customer = stripe.Customer.create(email='adam@telemericorp.com', api_key=STRIPE_SECRET_KEY)

# Use Stripe's dummy card data
DUMMY_CARD = {
    'number': '4242424242424242',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}

# You need a token for the customer in order to make a connect version of the customer
# The next line simulates the response from using stripe.js to tokenize a customer's card details
# You should not be replicating this on the server
pretendStripeJSToken = stripe.Token.create(api_key=STRIPE_SECRET_KEY, card=DUMMY_CARD)

# Your customer needs a card on file, and that's why we need that token
my_customer.cards.create(card=pretendStripeJSToken.id)

# Now we can charge this customer
i_get_ten_dollars = stripe.Charge.create(
    1000, 
    currency='usd', 
    customer=my_customer.id, 
    description='Frog toy', 
    api_key=STRIPE_SECRET_KEY
)

# And again.  Note we don't need any additional tokens or approval
my_money = stripe.Charge.create(
  100, 
  currency='usd', 
  customer=my_customer.id, 
  description='Money for me, the website creator',
  api_key=STRIPE_SECRET_KEY
)


# The customer MUST have a card on file before you can make a Shared Connect customer
# Need to create a Connect customer so the charges will go to our provider, not ourselves
connect_customer = stripe.Customer.create(
    card=customer_token.id, 
    email=my_customer.email, 
    api_key=connect_access_token ## <-- Note we are using the secret key from the OAuth flow
)
# THIS CONNECT_CUSTOMER HAS A TOTALLY DIFFERENT ID THAN MY_CUSTOMER.  
# IT CAN ONLY BE ACCESSED USING connect_access_token, NOT USING STRIPE_CUSTOMER_SECRET

# Even though the ID is different this connect_customer now has same credit card as my_customer
# If you charge connect_customer, it will be charged to that card
# This person got 90% off on their frog toy
connect_charge = stripe.Charge.create(
  amount=100, 
  currency='usd', 
  customer=connect_customer.id, ## <- PAY ATTENTION TO CUSTOMER IDs
  description='Frog toy', 
  api_key=connect_access_token ## <- PAY ATTENTION TO TOKENS
)

# Now that we've successfully charged them, lets add a new credit card
DUMMY_CARD2 = {
    'number': '5555555555554444',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}

# Add this card to their list.  It will be set as default.  If we charge them again,
# the charge will go on the card ending in 4444
# THIS DOES NOT UPDATE my_customer even though they're the same person.  Any update to
# a customer does not propagate to any other customer, even though they're related to 
# the same user
yetAnotherPretendJSKey = stripe.Token.create( # Note this is emulating stripe.js, not a server token creation
  card=DUMMY_CARD2, 
  api_key=STRIPE_SECRET_KEY
)
connect_customer.cards.create(card=yetAnotherPretendJSKey.id)

# We can create many connect customers even for the same vendors using the same email.
# In fact, if we call Customer.create again, we'll get another totally unrelated platform customer,
# even though they both have the same email and my_customer id
# Get a token
another_customer_token = stripe.Token.create(
  customer=my_customer.id, 
  api_key=connect_access_token
)

# Create the customer
another_connect_customer = stripe.Customer.create(
  card=another_customer_token.id, 
  email=my_customer.email, 
  api_key=connect_access_token
)

# Now we have two Connect customers that work just the same but have different IDs
connect_customer.id == another_connect_customer.id
# False

# Why would you ever do this? Stripe appears to invalidate your connect customers
# if the OAuth secret key changes, so sometimes you have to make new ones
# Other than that I don't know. 

# Now I can charge either whenever I want without any extra work.
# How nice
new_charge = stripe.Charge.create(
  amount=3200, 
  currency='usd', 
  customer=connect_customer.id,
  description='WoW Larping fees', 
  api_key=connect_access_token 
)
another_new_charge = stripe.Charge.create(
  amount=123000, 
  currency='usd', 
  customer=another_connect_customer.id,
  description='Bear Suit', 
  api_key=connect_access_token 
)


"""
 This next part is a shortcut if you don't want to save the customer. 
 You usually want to save them, because it streamlines the purchase
 process in the future, but if you want to make a single charge and forget 
their info forever, here's how
"""

# Make a token with your customer who already has a card attached
single_charge_token = stripe.Token.create(
  customer=my_customer.id,
  api_key=connect_access_token
)

# And now charge them.  Money goes to your vendor
single_charge = stripe.Charge.create(
  amount=400, 
  currency='usd', 
  card=single_charge_token.id, 
  description='single charge', 
  api_key=connect_access_token # <- Use key from OAuth
)