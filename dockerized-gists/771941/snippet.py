import os, sys
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders

SMTP_SERVER='localhost'

import mimetypes
mimetypes.init()

def send_mail(send_from, send_to, subject, text, files=[], server=SMTP_SERVER):
  assert type(files)==list

  msg = MIMEMultipart()
  msg['From'] = send_from
  msg['To'] = send_to # if multiple join with ', '
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = subject

  msg.attach( MIMEText(text) )

  for f in files:
    mtype = mimetypes.guess_type(f)[0]
    if mtype:
      part = MIMEBase(*mtype.split('/'))
    else:
      part = MIMEBase('application', "octet-stream")
    part.set_payload( open(f,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
    msg.attach(part)

  smtp = smtplib.SMTP(server)
  smtp.sendmail(send_from, send_to, msg.as_string())
  smtp.close()
  print 'Sent email to %s with attachments %s' % (send_to, files)


if __name__ == "__main__":
  _ ,send_from, send_to, subject, f = sys.argv
  send_mail(send_from, send_to, subject, "", [f])
