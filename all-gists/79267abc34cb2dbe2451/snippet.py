import datetime, time
import hangups
import plugins


def _initialise(bot):
    plugins.register_admin_command(["watermark", "typing"])


def watermark(bot, event, *args):
    yield from bot._client.updatewatermark(event.conv_id, datetime.datetime.fromtimestamp(time.time()))


def typing(bot, event, *args):
    yield from bot._client.settyping(event.conv_id, typing=hangups.schemas.TypingStatus.TYPING)