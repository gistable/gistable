# -*- coding: utf-8 -*-

import urllib, re, hashlib, os, smtplib
from email.MIMEText import MIMEText

class VisaChecker(object):
    """
    VisaChecker script for the applicants waiting 'administrative processing'.
    """
    
    LOG_FILE       = 'logs/latest_update.log'
    CONTROL_URL    = 'http://turkish.turkey.usembassy.gov/islemdeki_vize_istanbul.html'
    
    def __init__(self, config):
        """
        loads base configuration.
        
        @param config: dict
            - receipt_id,
            - gmail_username,
            - gmail_password,
            - target_email
        """
        self.receipt_id = config.get("receipt_id")
        
        if os.path.exists(VisaChecker.LOG_FILE) == False:
            open(VisaChecker.LOG_FILE, 'w+').close()

        self.gmail_login    = config.get("gmail_username")
        self.gmail_password = config.get("gmail_password")
        self.target_email   = config.get("target_email")

    def logLatestUpdateDate(self):
        """
        logs latest update date if there is a new entry.
        """
        page_content  = urllib.urlopen(VisaChecker.CONTROL_URL).read()
        latest_update = re.search('Son G&uuml;ncelleme:&nbsp;(.*?)<strong>', page_content).group(1)
        self.__controlCheckSum(latest_update, page_content)
    
    def __controlCheckSum(self, update_date, page_content):
        """
        calculates the latest update time string's md5sum and checks for a diff.
        """
        
        update_date_hash = hashlib.md5()
        update_date_hash.update(update_date)
        
        checksum  =  update_date_hash.hexdigest()
        checksums = open(VisaChecker.LOG_FILE).read().split("\n")
        
        if checksum not in checksums:
            file_handle = open(VisaChecker.LOG_FILE, 'a+')
            file_handle.write(checksum)
            file_handle.close()

            self.__controlIsIn(page_content)
        else:
            print 'herhangi bir guncelleme mevcut degil.'

            
    def __controlIsIn(self, content):
        if len(re.findall(str(self.receipt_id), content)) > 0:
            message = u'mujdemi isterim. size amerika yolu gozuktu.'
        else:
            message = u'uzucu bir haber vermek zorundayim ama guncellenen numaralarda da yoksunuz.'
        
        print message
            
        self.__sendEmail(message)
            
    def __sendEmail(self, message):
        msg            = MIMEText(message + u"\n\n lutfen kontrol ediniz:" + VisaChecker.CONTROL_URL)
        msg['Subject'] = "vizeler guncellendi."
        msg['From']    = self.gmail_login
        msg['To']      = self.target_email
     
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.gmail_login, self.gmail_password)
        server.sendmail(self.gmail_login, self.target_email, msg.as_string())
        server.close()


if __name__ == '__main__':
    visaChecker = VisaChecker({
        "receipt_id"     :  "1002745",
        "gmail_username" : "mail@emreyilmaz.me",
        "gmail_password" : "asdasd",
        "target_email"   : "mail@emreyilmaz.me",
    })
    visaChecker.logLatestUpdateDate()