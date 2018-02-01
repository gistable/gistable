import imaplib
import pygame

def cd_eject():
    pygame.cdrom.init()
    cd = pygame.cdrom.CD(0)
    cd.init()
    cd.eject()

def mail_check(user,passw):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user,passw)
    mail.select("Inbox")
    status,maillist = mail.search(None,"(UNSEEN)")
    if status == "OK":
        if maillist[0] is not '': cd_eject()
    mail.logout()

if __name__ == "__main__":
    mail_check("FIXME : hoge@gmail.com","FIXME : PASS")