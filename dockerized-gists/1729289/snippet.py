from BeautifulSoup import BeautifulSoup

body = "<p>Dear Everyone,</p><p>This is a test</p><h1>Test Complete</h1>"
plain_text = ' '.join(BeautifulSoup(body).findAll(text=True))