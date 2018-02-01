from fritzconnection import FritzConnection
import telepot
import re

connection = FritzConnection(password='YOUR_FROTS_PASSWORD')
ip = connection.call_action('WANPPPConnection', 'GetInfo')['NewExternalIPAddress']

match = re.search('^100\.', ip)

if match:
    bot = telepot.Bot('TELEGRAM_BOT_TOKEN');
    bot.sendMessage('@TELEGRAM_GROUP', 'I\'ve got IP: %s and I don\'t like it.' % ip)
    connection.reconnect()
