from functools import wraps

from telegram import ChatAction


def before_response(function):
    """Do something before responding"""

    def do_before(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                bot = args[0]
                update = args[1]
                function(bot, update)
            except (IndexError, AttributeError):
                msg = "Check if you spelled the attributes right and if this is \
                        applied to the right function."
                raise Exception(msg)
            return func(*args, **kwargs)
        return inner
    return do_before


def pre_response(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    
@before_response(pre_response)
def test(bot, update):
    pass


# Add command with CommandHandler etc