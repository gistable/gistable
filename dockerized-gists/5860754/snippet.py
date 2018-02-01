# python (flask) side:

import time
from flask import Response

app = Flask(__name__)

@app.route('/event_stream')
def stream():
    def event_stream():
        while True:
            time.sleep(3)
            yield 'data: %s\n\n' % 'hola mundo'

    return Response(event_stream(), mimetype="text/event-stream")

########################

# html side:

'''
<script>
  var source = new EventSource('/event_stream');
  source.onmessage = function(event){
    alert(event.data);
  };
</script>
'''

# if you want to support older browsers, also include this in your html:
# https://github.com/remy/eventsource-h5d/blob/master/public/EventSource.js