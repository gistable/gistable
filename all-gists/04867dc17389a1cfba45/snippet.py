import bottle
import requests

@bottle.route('/', method='POST')
def telegram_bot():
    data = bottle.request.json

    url = 'https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage'

    try:
        incoming_msg = data['message']['text']
        msg_from = data['message']['from'].get('username', data['message']['from']['first_name'])
    except Exception as e:
        print 'ERROR:', e
        print data
        incoming_msg = ''
        msg_from = 'friend'

    chat_id = data['message']['chat']['id']

    # private msg, prefix the command
    if chat_id > 0 and not incoming_msg.startswith('/autobot'):
        incoming_msg = '/autobot %s' % incoming_msg

    if (incoming_msg.startswith('/autobot') or '@autobot' in incoming_msg or
            incoming_msg.startswith('/help') or
            incoming_msg.startswith('/start')):
        outgoing_msg = 'Echo: message from:%s - %s' % (msg_from, incoming_msg)
        params = {
            'chat_id': chat_id,
            'text': outgoing_msg,
        }

        resp = requests.post(url, params)

    return 'hello'

application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(server='gunicorn', debug=True)