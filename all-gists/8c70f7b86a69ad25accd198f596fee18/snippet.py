import requests
import random
from faker import Faker
from bs4 import BeautifulSoup

def createAccount(email):
    fake = Faker()
    r = s.get("http://mydennys.ca/index")
    cook = r.cookies
    fname = fake.first_name()
    lname = fake.last_name()
    phone = genPhone() # 123+123+1234
    locale = "3"
    pin = fake.numerify(text="####")
    payload = {'customerFname': fname, 'customerLname': lname,
                'customerPhone': phone, 'customerEmail': email+"@gmail.com",
                'localeId': locale, 'customerPIN': pin, 'confirmPIN': pin,
                'promoCode': "", 'customerAgreeTerm': ""}
    r = s.post("http://mydennys.ca/auth/register", data=payload, cookies=cook)
    with open("accounts.txt", "a") as myfile:
        myfile.write(email + " " + pin + "\n")

def login(account): # line in file
    f = open('accounts.txt')
    lines = f.readlines()
    email, pin = lines[account].split(' ')
    print("Logged in as: {}".format(email))
    r = s.get("http://mydennys.ca/login")
    cook = r.cookies
    payload = {'eMail': email+"@gmail.com", 'customerPIN': pin}
    r = s.post("http://mydennys.ca/auth/auth", data=payload, cookies=cook)
    global globalAccount
    globalAccount = account

def logout():
    global globalAccount
    globalAccount = -1
    print("Logging out...")
    r = s.post("http://mydennys.ca/auth/logout", cookies=s.cookies)

def getPoints():
    # need to login first!
    if (globalAccount == -1):
        print("Log in to see how many points you have!")
        return False
    r = s.get("http://mydennys.ca/profile")
    soup = BeautifulSoup(r.text, "html.parser")
    points = soup.strong.string
    return points.replace(',', '')

def sendPoints(target, points): 
    # need to login first!
    if (globalAccount == -1):
        print("Log in before trying to send points!")
        return False
    if (points == "0"):
        print("No points to send")
        return False

    r = s.get("http://mydennys.ca/profile/gift")
    cook = r.cookies
    payload = {'targetCustomerEmail': target, 'points': points}
    r = s.post("http://mydennys.ca/profile/send_points", data=payload, cookies=cook)
    print(points + " points sent to " + target)

def vote():
    # need to login first!
    if (globalAccount == -1):
        print("Log in before trying to vote!")
        return False
    # get the poll page, and every valid poll ID
    r = s.get("http://mydennys.ca/votes", cookies=s.cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    polls = soup.findAll("a", {"class": "view", "title": "VIEW"})
    if (len(polls) == 0):
        print("No polls available")
        return False

    for i in polls:
        print("voting in {} polls".format(len(polls)))
        r = s.post("http://mydennys.ca/votes/view", data={"id": i['href']}, cookies=s.cookies)
        print("voting in poll... " + r.url)
        soup = BeautifulSoup(r.text, "html.parser")
        choice = soup.find("a", {"class": "vote", "title": "VOTE"})
        r = s.post("http://mydennys.ca/votes/vote", data={"pollChoiceId": choice['href']}, cookies=s.cookies)

def genPhone():
    first = str(random.randint(100,999))
    second = str(random.randint(1,888)).zfill(3)

    last = (str(random.randint(1,9998)).zfill(4))
    while last in ['1111','2222','3333','4444','5555','6666','7777','8888']:
        last = (str(random.randint(1,9998)).zfill(4))

    return '{}+{}+{}'.format(first,second, last)

s = requests.Session()
for i in range(0, 200):
    createAccount("example+" + i) # create accounts with example+1@gmail.com etc...
    globalAccount = -1 # line in file, if -1 exit functions that require login
    login(i)
    vote()
    sendPoints("example@gmail.com", getPoints())
    logout()


