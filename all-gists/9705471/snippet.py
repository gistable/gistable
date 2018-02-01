"""

ledctrl.py

A simple example for communicating with a Raspberry Pi from you phone's 
browser. Uses the Bottle Python web framework, and jQuery AJAX.

Author: Mahesh Venkitachalam / electronut.in
"""

from bottle import route, request, run, get

import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, False)

@route('/led')
def led():
    return '''
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="http://code.jquery.com/mobile/1.4.2/jquery.mobile-1.4.2.min.css">
<script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>
<script src="http://code.jquery.com/mobile/1.4.2/jquery.mobile-1.4.2.min.js"></script>
<script>
$(document).ready(function() {
  $("#ckLED").change(function() {
    var isChecked = $("#ckLED").is(":checked") ? 1:0; 
    $.ajax({
            url: '/action',
            type: 'POST',
            data: { strID:'ckLED', strState:isChecked }
    });
  });
});
</script>
</head>

<body>

<div data-role="page">
  <div data-role="main" class="ui-content">
    <form>
        <label for="switch">RPi LED Control</label>
        <input type="checkbox" data-role="flipswitch" name="switch" id="ckLED">
    </form>
 </div>
</div>

</body>
</html>
'''

@route('/action', method='POST')
def action():
    val = request.forms.get('strState')
    on = bool(int(val))
    GPIO.output(18, on) 

run(host = '192.168.4.31', port = '8080')
