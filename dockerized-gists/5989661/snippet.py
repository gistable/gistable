#-*- coding:utf-8 -*-

import time
import subprocess

"""
select last_name || "" || middle_name || "" || first_name as name, mobile_phone, other_phone from contacts where categories like "%通讯录%" and (mobile_phone <> '' or other_phone <> '')
"""

people = [
    (p["name"], p["mobile_phone"], p["other_phone"]) for p in
    { "name" : """Example""", "mobile_phone" : """+86 138 0013 8000""", "other_phone" : """10086""" },
    { "name" : """Example""", "mobile_phone" : """+86 138 0013 8000""", "other_phone" : """10086""" }
]


def generate_messages():
    for name, mobile_phone, other_phone in people:
        short_number = mobile_phone if 0 < len(mobile_phone) < 8 else other_phone
        has_long_number = len(mobile_phone) > 8
        mobile_phone = mobile_phone.replace("+86", "").replace(" ", "")

        msg = ("%s你好,我是XXX,此刻已经离开深圳赴京求职." % name +
               "我原来的联系方式是13800138000(短号10086)," +
               "从0月00日开始将被新的电话号码13600000000取代," +
               "短号也将关停,请更新通讯录.")
        if short_number:
            print("[%s]" % short_number)
            msg += ("我曾记录你的短号是%s," % short_number +
                    ("但缺失了长号.如果你愿意,烦请回复联系电话长号给我." if not has_long_number else
                    "长号是%s,如果长号已经更新,烦请回复新号码." % mobile_phone) +
                    "我的邮箱example@example.com" +
                    "将长期不变,通过它们也能联系到我.")
        else:
            print("[%s]" % mobile_phone)

        msg += "[由土法自制机器人发送]"

        print msg, "[%d个字]" % len(msg.decode("utf8"))
        print "---"

        yield short_number or mobile_phone, msg


def send_sms(phone, body):
    subprocess.call(["adb", "shell", "am", "start",
                     "-a", "android.intent.action.SENDTO",
                     "-d", "sms:%s" % phone,
                     "--es", "sms_body", '"%s"' % body,
                     "--ez", "exit_on_sent", "true"])
    subprocess.call(["adb", "shell", "sleep", "1"])
    subprocess.call(["adb", "shell", "input", "keyevent", "22"])
    subprocess.call(["adb", "shell", "sleep", "1"])
    subprocess.call(["adb", "shell", "input", "keyevent", "66"])


def prompt_ok(message, default=False):
    suffix = "[y/N]" if not default else "[Y/n]"
    while True:
        user_input = raw_input("%s? %s: " % (message, suffix))
        if not user_input:
            return bool(default)
        if user_input.strip() in ("n", "N"):
            return False
        if user_input.strip() in ("y", "Y"):
            return True


if __name__ == "__main__":
    while not prompt_ok("请点亮手机屏幕并呆在 Home 界面,准备好了吗"):
        pass

    for phone, msg in generate_messages():
        if prompt_ok("确认发送", default=True):
            send_sms(phone, msg)
