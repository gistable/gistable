"""
This is a script to help James find a global entry appointment before September because
the whole tsa global entry thing is fucked.

To use:

sudo pip install scrapy
scrapy runspider global_entry_scrapper.py

To set up automated email notifications:

sudo yum install python-pip -y
sudo yum install python-devel -y
sudo yum install gcc gcc-devel -y
sudo yum install libxml2 libxml2-devel -y
sudo yum install libxslt libxslt-devel -y
sudo yum install openssl openssl-devel -y
sudo yum install libffi libffi-devel -y
CFLAGS="-O0" sudo pip install lxml
sudo pip install Scrapy

crontab -e
*/15 * * * * scrapy runspider global_entry_scrapper.py

"""

USERNAME = ''
PASSWORD = '' # special shitty password for global entry
TEST_CENTER = '5446'  #SFO
RUN_EMAIL_NOTIFICATION = False
EMAIL = 'hng.jms@gmail.com'

import scrapy
import os

class GlobalEntrySpider(scrapy.Spider):
    name = 'globalentryspider'
    start_urls = ['https://goes-app.cbp.dhs.gov/main/goes']

    def parse(self, response):
        return [scrapy.FormRequest.from_response(
                response,
                formnumber=0,
                formdata={'username': USERNAME, 'password': PASSWORD},
                callback=self.after_login)]

    def after_login(self, response):
        return scrapy.Request("https://goes-app.cbp.dhs.gov/main/goes/HomePagePreAction.do",
                              callback=self.process_landing_page)

    def process_landing_page(self, response):
        return [scrapy.FormRequest.from_response(
                response,
                formnumber=0,
                formdata={
                    'actionFlag': 'existingApplication',
                    'homepageProgramIndex': '0',
                },
                callback=self.process_scheduled_interviewed_page)]

    def process_scheduled_interviewed_page(self, response):
         return [scrapy.FormRequest.from_response(
                response,
                formnumber=0,
                formdata={
                    'actionFlag': 'reschedule'
                },
                callback=self.process_center_selection_page)]

    def process_center_selection_page(self, response):
        return [scrapy.FormRequest.from_response(
                response,
                formnumber=0,
                formdata={
                    'forwardFlag': 'next',
                    'selectedEnrollmentCenter': TEST_CENTER,
                },
                callback=self.wip)]

    def wip(self, response):
        availibility = False
        print "--"*200
        COOL_MONTHS = ['May', 'June', 'July', 'August']
        for month in COOL_MONTHS:
            if month in response.body:
                availiblity = True
                print "Availible slot in :", month
            else:
                print "No availiblity in :", month
        print "--"*200
        if RUN_EMAIL_NOTIFICATION and availiblity:
            os.system("""echo "go reschedule your global entry apt." | mail -s "global entry availibility" """ + EMAIL)
