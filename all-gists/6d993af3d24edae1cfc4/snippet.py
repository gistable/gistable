import smtplib
from getpass import getpass

def prompt(prompt):
    return input(prompt).strip()

fromaddr = prompt("From: ")
toaddrs  = prompt("To: ").split()
subject  = prompt("Subject: ")
print("Enter message, end with ^D (Unix) or ^Z (Windows):")

# Add the From: To: and Subject: headers at the start!
msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs), subject))
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print("Message length is", len(msg))

server = smtplib.SMTP_SSL('smtp.qq.com')
# 如果是其他的服务，只需要更改 host 为对应地址，port 对对应端口即可
# server = smtplib.SMTP_SSL(host='smtp.qq.com', port=465)
server.set_debuglevel(1)    # 开启调试，会打印调试信息
print("--- Need Authentication ---")
username = prompt("Username: ")
password = getpass("Password: ")
server.login(username, password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
