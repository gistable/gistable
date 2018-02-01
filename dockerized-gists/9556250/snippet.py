from flask import Flask, request
chat = Flask(__name__)

html = """
<html><head><style>
#mychat{width:100%; font-size: 15px; padding: 10px; border: 1px solid #111111;}
</style></head><body>
	<input id="mychat" placeholder="Type message and press enter"/>
	<div id="chat"></div>
	<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
	<script>
	$('#mychat').keypress(function(e){
		if( e.keyCode==13 ){
			$.get('/send',{msg:$('#mychat').val()});
			$('#mychat').val('');
		}
	});
	last = 0;
	setInterval(function(){
		$.get('/update',{last:last},
			function(response){
				last = $('<p>').html(response).find('span').data('last');
				$('#chat').append(response);
				$('span:not(:last)').remove();
				});
		},1000);
	</script>
</body></html>
"""

msgs = []

@chat.route('/')
def index():return html

@chat.route('/send')
def send():
	msgs.append('%s:%s' % (request.remote_addr, request.args['msg']))
	return ""

@chat.route('/update')
def update():
	updates= msgs[int(request.args['last'])::]
	last = "<span data-last='%s'></span>" % len(msgs)
	if len(updates) > 0:
		return "<br>".join(updates) + last + "<br>"
	else:
		return last

if __name__ == '__main__': chat.run()