"""
pybble.py

Yup, you can run Python on your Pebble too! Go thank the good folks who
made Transcrypt, a dead-simple way to take your Python code and translate
it to *very* lean Javascript. In our case, instead of browser, we run it
on Pebble using their equally dead-simple Online IDE and Pebble.js library.

Here's a working example, it runs on a real Pebble Classic.

Usage:
    1. Install transcrypt  (You should use a Python virtual environment)
        pip install transcrypt
    2. Python becomes Javascript
        transcrypt pybble.py
    3. Get the (minified) source code
        - on MacOS
            cat __javascript__/pybble.min.js | pbcopy
            OR
            open __javascript__/pybble.min.js
        - On other OSes, copy the content, or optn the file in an editor and do so
            cat __javascript__/pybble.min.js
    4. Create a new project on https://cloudpebble.net
        - Select Pebble.js as the project type
        - Open `app.js` and replace the example code with the code you copied.
    5. Click the Run button
    6. :-D
"""

ajax = require('ajax')
_UI = require('ui')

__pragma__('kwargs')


class UI(object):
    @classmethod
    def Window(**kwargs):
        return __new__(_UI.Window(kwargs))

    @classmethod
    def Card(**kwargs):
        return __new__(_UI.Card(kwargs))


__pragma__('nokwargs')


def on_select_click(e):
    def callback(data):
        quote = data['contents']['quotes'][0]['quote']
        author = data['contents']['quotes'][0]['author']
        card = UI.Card(title='QOD', subtitle=author, body=quote)
        card.show()

    ajax({'url': 'http://api.theysaidso.com/qod.json',
          'type': 'json'}, callback)


main = UI.Card(title='It Works!',
                    subtitle='Python on Pebble',
                    body='Press Select for Quote of The Day')

main.on('click', 'select', on_select_click)
main.show()
