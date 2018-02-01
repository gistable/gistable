#!/usr/bin/python2
# coding=utf-8
import csv
import datetime
import codecs
import smtplib
import traceback
import os.path
from email.mime.text import MIMEText

SMTP_SERVER = 'localhost'
MAIL_FROM = 'info@linuq.org'
MAIL_SUBJECT = u"avis d'expiration de votre compte"

NOTIFIED_SEP = ' : '
NOTIFIED_FILE = 'notifications.txt'

DATE_FORMAT = '%Y-%m-%d'
CSV_FILE = 'Liste_membres.csv'
CSV_FIELDS = [
    'last_name',
    'first_name',
    'expiration_old',
    'subscription',
    'expiration',
    'student',
    'telephone',
    'email',
]
SKIP_ROWS = 2

NB_DAYS_WARNING = [0, 10, 30]
NB_DAYS_EXPIRE = 365

TEXT_WARNING = u"""Bonjour %(name)s,

Ceci est un message automatisé pour vous avertir 
que votre abonnement expirera dans moins de %(nb_days)d jours, 
soit le %(expire_date)s.

Si vous avez des questions, vous pouvez écrire à info@linuq.org.

Bonne journée
"""

TEXT_EXPIRED = u"""Bonjour %(name)s,

Ceci est un message automatisé pour vous avertir 
que votre abonnement a expiré depuis le %(expire_date)s.

Si vous avez des questions, vous pouvez écrire à info@linuq.org.

Bonne journée
"""

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.line_num = 0

    def next(self):
        row = self.reader.next()
        self.line_num += 1
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class DictReader(csv.DictReader):
    """
    HACK: csv.DictReader is hardcoded to take a filename as reader param.
    The __init__ redefined here is a workaround
    """
    def __init__(self, reader, fieldnames, restkey=None, restval=None, 
            dialect='excel', *args, **kwargs):

        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.dialect = dialect
        self.line_num = 0
        if isinstance( reader, str ) or isinstance( reader, unicode ):
            self.reader = csv.reader( reader, *args, **kwargs )
        else:
            self.reader = reader

class ExpirationScanner(object):
    """
    Opens a CSV file with LinuQ accounts and
    scans for memberships that will expire soon
    """
    def __init__(self, limit, warnings):
        """
        limit: (int) number of days a membership lasts
        warnings (list) number of days before expiration where we would like to warn the user
        dt_format : (string) date format (see datetime.datetime.strptime)
        csv_fields : (list) name of fields in the csv file
        """
        self.limit = datetime.timedelta( days = limit )
        warnings.sort()
        self.warnings = [ datetime.timedelta( days = x ) for x in warnings ]
        self.today = datetime.date.today()

    def _find_closest_warning(self, expires_at):
        for warning in self.warnings:
            if expires_at - warning <= self.today:
                return warning.days
        return None

    def scan(self, filename, fields, date_col, date_format, skip_rows=2):
        """
        Scan a csv file and return the rows that will expire soon
        csv_filename : filename
        date_col : name of the column that contains the subscription date
        """
        expired = []
        reader = DictReader( UnicodeReader( open( filename, 'r') ), fields )

        for x in range( skip_rows ):
            reader.next()

        for row in reader:
            #subscribed_at = datetime.datetime.strptime( row[date_col], date_format ).date()
            #expires_at = subscribed_at + self.limit
            expires_at = datetime.datetime.strptime( row[date_col], date_format ).date()
            #If you prefer retreiving the expiration date directly from the CSV, uncomment the following line:
            #expires_at = datetime.date.strptime( row[date_col], date_format ).date()
            warning = self._find_closest_warning( expires_at )
            if warning is not None:
                expired.append( (warning, expires_at, row) )
        return expired

class SMTPSender(object):
    """
    Simple wrapper around smtplib and MIMEText for sending emails
    """
    def __init__(self, server, port=25, tls=False, user=None, password=None):
        self.server = server
        self.port = port
        self.tls = tls
        self.user = user
        self.password = password

    def send(self, addr_from, addr_to, subject, text):

        print text
        print
        #import pdb; pdb.set_trace()
        msg = MIMEText(text.encode('utf-8'), _charset='utf-8')
        msg['From'] = addr_from
        msg['To'] = addr_to
        msg['Subject'] = subject

        conn = smtplib.SMTP(self.server, self.port)
        if self.tls:
            conn.starttls()
        conn.ehlo_or_helo_if_needed()
        if self.user and self.password:
            conn.login( self.user, self.password )
        conn.sendmail( addr_from, addr_to, msg.as_string() )
        

def read_notified_file( filename ):
    """
    transform a file containing a list of people already notified 
    into a dict
    """
    notified = {}
    if os.path.isfile( filename ):
        with open( filename, 'r' ) as f:
            for line in f:
                line = unicode( line, encoding='utf-8' )
                user, warning = line.split(NOTIFIED_SEP)
                notified[user] = int(warning)
    return notified

def write_notified_file( filename, notified ):
    """
    write dict containing info on people who have been notified 
    and the number of days left before their membership expires.
    key : username | value : number of days left
    """
    with open( filename, 'w' ) as f:
        for key, value in notified.iteritems():
            line = ( "%s%s%s\n" % (key, NOTIFIED_SEP, value) ).encode('utf-8')
            f.write( line )

def main():
    smtp = SMTPSender( SMTP_SERVER )
    scanner = ExpirationScanner( NB_DAYS_EXPIRE, NB_DAYS_WARNING )
    notified = read_notified_file( NOTIFIED_FILE )
    expired = scanner.scan( CSV_FILE, CSV_FIELDS, 'expiration', DATE_FORMAT, SKIP_ROWS )

    names = set()
    today = datetime.date.today()
    
    for warning, expires_at, row in expired:
        name = "%s %s" % (row['first_name'], row['last_name'])
        names.add( name )
        if expires_at <= today and name not in notified:
            smtp.send(
                MAIL_FROM,
                row['email'],
                MAIL_SUBJECT,
                TEXT_EXPIRED % {'expire_date' : expires_at.strftime( DATE_FORMAT ), 'name' : name }
            )
            notified[name] = warning
        elif name not in notified or int( notified[name] ) > warning:
            smtp.send(
                MAIL_FROM,
                row['email'],
                MAIL_SUBJECT,
                TEXT_WARNING % {'expire_date' : expires_at.strftime( DATE_FORMAT ), 'nb_days' : warning, 'name' : name }
            )
            notified[name] = warning      

    #Remove entries that are no longer in the csv or have renewed their subscription
    for key in ( set( notified.keys() ).difference( names ) ):
        del notified[key]

    write_notified_file( NOTIFIED_FILE, notified )

if __name__ == '__main__':
    try:
        main()
    except:
        smtp = SMTPSender( SMTP_SERVER )
        smtp.send( 
            MAIL_FROM, 
            MAIL_FROM, 
            'notifications expiration erreur', 
            "Une erreur est survenu lors de l'execution du script: %s" % traceback.format_exc()
        )