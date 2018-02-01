from __future__ import print_function
import base64, urllib, urllib2

api_key = "api:" + "key-MAILGUN_KEY"
routes_url = 'http://mailgun.net/api/routes.xml'
messages_url = 'http://mailgun.net/api/messages.txt'

def create_routes(pattern, destination):
    post_headers = {
    'Authorization': 'Basic {0}'.format(base64.b64encode(api_key)),
    'Content-Type' : 'text/xml'
    }
    post_data = """<route><pattern>{0}</pattern><destination>{1}</destination></route>""".format(pattern,destination)
    req = urllib2.Request(routes_url, post_data, post_headers)
    response = urllib2.urlopen(req)
    html = response.read()
    print(html)
    print("Route has been successfully added")
    return html

def send_email(address, subject):
    post_data = {
        'servername': 'todo.kiarash.me',
        'sender': 'server@todo.kiarash.me',
        'recipients': address,
        'subject': subject,        
        'body': 'Here is the forwarder email!'
        }

    headers = {
        'Authorization': 'Basic {0}'.format(base64.b64encode(api_key)), 
        'Content-Type': 'application/x-www-form-urlencoded'
        }

    post_data = urllib.urlencode(post_data)
    req = urllib2.Request(messages_url, post_data, headers)
    response = urllib2.urlopen(req)
    html = response.read()
    print(html)
    print("Text message has been successfully sent via send_text")
    return html

def lambda_handler(event, context):
    try: 
        from_email = event["from_email"]
        forward_to = event["forward_to"]
    except:
        raise ValueError('Missing params!')

    # All new emails sent to "from_email" will be forwarded to "forward_to".
    routes_html = create_routes(pattern=from_email, destination=forward_to)

    # Send an email to the "forward_to" email, putting "from_email" in the subject line.
    email_html = send_email(address=forward_to, subject=from_email)

    return "DONE \n" + routes_html + "\n" + email_html