# Project Structure
facebook/
        runserver.py
        feed/
            __init__.py
            views.py
        chat/
            __init__.py
            views.py
            

# create blueprint in feed/__init__.py
from flask import Blueprint

feed = Blueprint('feed', __name__)
import views

# create blueprint in chat/__init__.py
from flask import Blueprint

chat = Blueprint('chat', __name__)
import views

# add views (endpoints) in feed/views.py
from . import feed

@feed.route('/feed')
def feed():
    return 'feed'
    
# add views (endpoints) in chat/views.py
from . import chat

@chat.route('/chat')
def chat():
    return 'chat'


# register blueprint and start flask app
from flask import Flask
from expense import expense
from budget import budget

app = Flask(__name__)
app.register_blueprint(feed)
app.register_blueprint(chat)
app.run(debug=True)

# In Action
 * Running on http://127.0.0.1:5000/
# Hit Urls
http://127.0.0.1:5000/feed # output feed
http://127.0.0.1:5000/chat # output chat