'''
This is an example of the server-side logic to handle slash commands in
Python with Flask.
Detailed documentation of Slack slash commands:
https://api.slack.com/slash-commands
Slash commands style guide:
https://medium.com/slack-developer-blog/slash-commands-style-guide-4e91272aa43a#.6zmti394c

'''

# import your app object
from flask import request, jsonify, abort

# The parameters included in a slash command request (with example values):
#   token=gIkuvaNzQIHg97ATvDxqgjtO
#   team_id=T0001
#   team_domain=example
#   channel_id=C2147483705
#   channel_name=test
#   user_id=U2147483697
#   user_name=Steve
#   command=/weather
#   text=94070
#   response_url=https://hooks.slack.com/commands/1234/5678

@app.route('/slash-command-url', methods=['POST'])
def slash_command():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    # Parse the parameters you need
    token = request.form.get('token', None)  # TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)
    # Use one of the following return statements
    # 1. Return plain text
    return 'Simple plain response to the slash command received'
    # 2. Return a JSON payload
    # See https://api.slack.com/docs/formatting and
    # https://api.slack.com/docs/attachments to send richly formatted messages
    return jsonify({
        # Uncomment the line below for the response to be visible to everyone
        # 'response_type': 'in_channel',
        'text': 'More fleshed out response to the slash command',
        'attachments': [
            {
                'fallback': 'Required plain-text summary of the attachment.',
                'color': '#36a64f',
                'pretext': 'Optional text above the attachment block',
                'author_name': 'Bobby Tables',
                'author_link': 'http://flickr.com/bobby/',
                'author_icon': 'http://flickr.com/icons/bobby.jpg',
                'title': 'Slack API Documentation',
                'title_link': 'https://api.slack.com/',
                'text': 'Optional text that appears within the attachment',
                'fields': [
                    {
                        'title': 'Priority',
                        'value': 'High',
                        'short': False
                    }
                ],
                'image_url': 'http://my-website.com/path/to/image.jpg',
                'thumb_url': 'http://example.com/path/to/thumb.png'
            }
        ]
    })
    # 3. Send up to 5 responses within 30 minutes to the response_url
    # Implement your custom logic here
