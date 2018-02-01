import re

WORDS = ["INTRODUCE", "YOURSELF", "DAVY"]

PRIORITY = 3

def handle(text, mic, profile):
    messages = ["Hi, I'm Davy. Nice to meet you.",
                "Okay, I'm Davy."]

    message = random.choice(messages)

    mic.say(message)
    
def isValid(text):
    return bool(re.search(r'\bintroduction\b', text, re.IGNORECASE))