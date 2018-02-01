"""
Simple demonstration of how to implement Server-sent events (SSE) in Python
using Bottle micro web-framework.

SSE require asynchronous request handling, but it's tricky with WSGI. One way
to achieve that is to use gevent library as shown here.

Usage: just start the script and open http://localhost:8080/ in your browser.

Based on:
- "Primer to Asynchronous Applications",
	http://bottlepy.org/docs/dev/async.html
- "Using server-sent events",
	https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events
"""


# Bottle requires gevent.monkey.patch_all() even if you don't like it.
from gevent import monkey; monkey.patch_all()
from gevent import sleep

from bottle import get, post, request, response
from bottle import GeventServer, run


sse_test_page = """
<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8" />
		<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/1.8.3/jquery.min.js "></script>
		<script>
			$(document).ready(function() {
				var es = new EventSource("stream");
				es.onmessage = function (e) {
					$("#log").html($("#log").html()
						+ "<p>Event: " + e.event + ", data: " + e.data + "</p>");
				};
			})
		</script>
	</head>
	<body>
		<div id="log" style="font-family: courier; font-size: 0.75em;"></div>
	</body>
</html>
"""


@get('/')
def index():
	return sse_test_page


@get('/stream')
def stream():
	# "Using server-sent events"
	# https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events
	# "Stream updates with server-sent events"
	# http://www.html5rocks.com/en/tutorials/eventsource/basics/

	response.content_type  = 'text/event-stream'
	response.cache_control = 'no-cache'

	# Set client-side auto-reconnect timeout, ms.
	yield 'retry: 100\n\n'

	n = 1

	# Keep connection alive no more then... (s)
	end = time.time() + 60
	while time.time() < end:
		yield 'data: %i\n\n' % n
		n += 1
		sleep(1)


if __name__ == '__main__':
	run(server=GeventServer)
