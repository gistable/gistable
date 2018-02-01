"""
execute w and df -h on server
"""
import plugins
import subprocess


def _initialize(bot):
    plugins.register_admin_command(['w'])
    plugins.register_admin_command(['df'])


def w(bot, event, *args):
    string = subprocess.Popen(["w"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").replace("\n","<br><br>")
    yield from bot.coro_send_message(event.conv_id, string)

def df(bot, event, *args):
    string = subprocess.Popen(["df","-h"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").replace("\n","<br><br>")
    yield from bot.coro_send_message(event.conv_id, string)