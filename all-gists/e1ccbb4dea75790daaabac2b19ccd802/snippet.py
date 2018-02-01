from xml.etree import ElementTree as ETree

from wxpy import *

bot = Bot()


# 通过 NOTE 消息找到 bot.messages 中被撤回的消息
# 并转发到机器人的文件传输助手

@bot.register(msg_types=NOTE)
def get_revoked(msg):
    # 检查 NOTE 中是否有撤回信息
    revoked = ETree.fromstring(msg.raw['Content']).find('revokemsg')
    if revoked:
        # 根据找到的撤回消息 id 找到 bot.messages 中的原消息
        revoked_msg = bot.messages.search(id=int(revoked.find('msgid').text))[0]
        # 原发送者 (群聊时为群员)
        sender = msg.member or msg.sender
        # 把消息转发到文件传输助手
        revoked_msg.forward(
            bot.file_helper,
            prefix='{} 撤回了:'.format(sender.name)
        )


embed()
