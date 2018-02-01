#coding=utf8
import itchat, time

SINCERE_WISH = u'祝%s新年快乐！'
REAL_SINCERE_WISH = u'祝%s新年快乐！！'

def send_wishes():
    friendList = itchat.get_friends(update=True)[1:]
    for friend in friendList:
        # 如果不是演示目的，把下面的方法改为itchat.send即可
        print(SINCERE_WISH % (friend['DisplayName']
            or friend['NickName']), friend['UserName'])
        time.sleep(.5)

def send_special_wishes(chatroomName='wishgroup'):
    itchat.get_chatrooms(update=True)
    chatrooms = itchat.search_chatrooms(name=chatroomName)
    if chatrooms is None:
        print(u'没有找到群聊：' + chatroomName)
    else:
        chatroom = itchat.update_chatroom(chatrooms[0]['UserName'])
        for friend in chatroom['MemberList']:
            friend = itchat.search_friends(userName=friend['UserName'])
            # 如果不是演示目的，把下面的方法改为itchat.send即可
            print(REAL_SINCERE_WISH % (friend['DisplayName']
                or friend['NickName']), friend['UserName'])
            time.sleep(.5)

itchat.auto_login(True)

send_wishes()
send_special_wishes()