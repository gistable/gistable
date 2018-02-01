import notifs

def print_notification(title, message):
  print "Notification received: {0}: {1}".format(title, message)

def web_app_notify(title, message):
  print "Webapp notification received: {0}: {1}".format(title, message)

def iphone_app_notify(title, message):
  print "iPhone App notification received: {0}: {1}".format(title, message)

def android_app_notify(title, message):
  print "Android App notification received: {0}: {1}".format(title, message)

try:
  n = notifs.Notifs("amqps://user:password@domain.tld:5673/%2F")
  n.receive("routing_name", print_notification)
  n.receive("routing_name", web_app_notify)
  n.receive("routing_name", iphone_app_notify)
  n.receive("routing_name", android_app_notifify)

except KeyboardInterrupt:
  break

# https://github.com/andreimarcu/aamnotifs
# https://news.ycombinator.com/item?id=6109977    