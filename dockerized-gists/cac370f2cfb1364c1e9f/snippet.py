# coding: utf-8
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup


class Settings(object):
    """Mail config"""
    MAIL_HOST = "smtp.example.com"
    MAIL_USER = "yourname@example.com"
    MAIL_PASS = "password"
    MAILTO_LIST = ["yourname@example.com", ]
    GREP_URL = 'https://www.packtpub.com/packt/offers/free-learning'


def grep_new_free_book():
    try:
        r = requests.get(url=Settings.GREP_URL)
    except Exception, e:
        return False
    if r.status_code != 200:
        return False
    soup = BeautifulSoup(r.content)
    book_name = soup.find('div', class_='dotd-title').get_text(strip=True)
    cover_img = soup.find('img', class_='bookimage imagecache imagecache-dotd_main_image')
    cover_url = cover_img.get('src')
    email_content = """
        <h1>The Free Book today</h1>
        <img src="http:%s" alt="">
        <p>%s</p>
        <a href="%s">Click Here to get the book</a>
        """ % (cover_url, book_name, Settings.GREP_URL)
    return sendmail(email_content)


def sendmail(email_content):
    msg = MIMEText(email_content, _subtype='html', _charset='utf-8')
    msg['Subject'] = 'New Free Book'
    msg['From'] = "yourname" + "<" + Settings.MAIL_USER + ">"
    msg['To'] = ";".join(Settings.MAILTO_LIST)
    try:
        s = smtplib.SMTP()
        s.connect(Settings.MAIL_HOST)
        s.login(Settings.MAIL_USER, Settings.MAIL_PASS)
        s.sendmail(msg['From'], Settings.MAILTO_LIST, msg.as_string())
        s.close()
    except Exception, e:
        return False
    return

if __name__ == '__main__':
    grep_new_free_book()
