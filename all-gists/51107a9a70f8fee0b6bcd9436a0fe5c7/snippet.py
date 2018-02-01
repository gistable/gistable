from functools import wraps

from telegram.ext import Updater, CommandHandler

# Using a factory function (closures) to contain the started-state of the bot
# This is cleaner and better-practice than using globals
def state_factory():
    """Factory function for containing the bot state."""

    state = False

    def switch_state():
        nonlocal state
        state = not state

    def get_state():
        nonlocal state
        return state

    return (switch_state, get_state)


def is_started(func):
    """Check wether the bot is started."""

    @wraps(func)
    def inner(*args, **kwargs):
        if get_state():
            return func(*args, **kwargs)
    return inner


def start(bot, update):
    """Start the bot."""

    if not get_state():
        switch_state()
        msg = "Started, sir."
        update.message.reply_text(msg)
        
        
def stop(bot, update):
    """Stop the bot."""

    if get_state():
        switch_state()
        msg = "Stopped, sir."
        update.message.reply_text(msg)
        
        
@is_started
def test(bot, update):
    """Test if the started decorator works."""
    
    update.message.reply_text("Test!")
    
def main():
    """Initialize the commands."""
    
    start_handler = CommandHandler("start", start)
    stop_handler = CommandHandler("stop", stop)
    test_handler = CommandHandler("test", test)
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(test_handler)
    

if __name__ == "__main__":
    # Start the bot!
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))
    dispatcher = updater.dispatcher
    switch_state, get_state = state_factory()
    main()