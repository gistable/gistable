import re

WORDS = ["YOUR", "FAVORITE", "COLOR"]

PRIORITY = 3

def handle(text, mic, profile):
    messages = ["I would tell you but you wouldn't be able to comprehend it."]

    mic.say(message)
    
def isValid(text):
    return bool(re.search(r'\bfavorite color\b', text, re.IGNORECASE))