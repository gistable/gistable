#!/usr/bin/env python
# -*- coding: utf-8 -*-
## Versao 0.25

"""
Script de Backup MYSQL (backup_mysq.py)
Copyrighted by Nilton OS <jniltinho at gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 Colocar no Crontab
 Script para Backup do Mysql
 05 01 * * * /usr/local/bin/backup_mysql.py --backup
 
 Como utilizar:
 - Configure corretamente os dados de e-mail, se quizer enviar e-mail
 - python backup_mysql.py --backup --debug
 - Ele uso o comando do sistema mysqldump do MYSQL
 - Para enviar e-mail execute o comando abaixo
 - python backup_mysql.py --backup --debug --sendmail
  
"""


import os, sys, optparse, socket
import commands, time


#from smtplib import SMTP_SSL as SMTP       #secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP                    #standard SMTP protocol (port 25,587, no SSL)
from email.MIMEText import MIMEText

#---------------------------------------------------------------------------
## esses campos podem ser alterados
user_mysql  = 'root'
pass_mysql  = 'senha_do_root'
host_mysql  = 'localhost'
hostname    = socket.gethostname()
backup_dir  = '/usr/local/backup/mysql'
log_file    = '/var/log/backup_mysql.log'
l_hostname  = hostname
SMTPserver  = 'smtp.dominio.com.br'
sender      = 'email@dominio.com.br'
USERNAME    = 'email@dominio.com.br'
PASSWORD    = 'senha_email'
destination = ['email1@dominio_x.com.br']
des_ccc     = ['admin@dominio_y.com.br']
#---------------------------------------------------------------------------
verbose    = False
message    = ''
filestamp  = time.strftime('%Y%m%d_%H%M')


def exec_backup(BackupDir):
    # Get a list of databases with :
    if not os.path.lexists(BackupDir): os.makedirs(BackupDir)
    database_list_command="mysql -u %s -p%s -h %s --silent -N -e 'show databases'" % (user_mysql,pass_mysql, host_mysql)
    for database in os.popen(database_list_command).readlines():
        database = database.strip()
        if database in ['Database','information_schema','test','performance_schema']:
            continue
        filename = "%s/%s-%s.sql" % (backup_dir, database, filestamp)
        cmd = ("mysqldump -u %s -p%s -h %s -e --opt -B -R -c %s | gzip -c > %s.gz" % (user_mysql, pass_mysql, host_mysql, database, filename))
        log("BACKUP BANCO: %s ARQUIVO: %s.gz" %(database, filename))
        cmd_result = commands.getoutput(cmd)
        log(cmd_result)
        #print ("%s -p%s -h %s -e --opt -c %s %s.gz" % (username, password, hostname, database, filename))


def check_mysql():
    log("Checando as Bases de Dados do MYSQL")
    cmd = ("mysqlcheck -u %s -p%s -h %s --all-databases --auto-repair" % (user_mysql, pass_mysql, host_mysql))
    cmd_result = commands.getoutput(cmd)
    log(cmd_result)


def log(mes):
    global message
    str = ("%s - %s\n") %(time.strftime('%b %d %H:%M:%S'), mes)
    message += str
    if verbose: str = str.rstrip("\n"); print str


def send_mail(receiver, Subject):
    global message
    subject   = ("%s JOB: %s HOST: %s") %(Subject, sys.argv[0], hostname)
    receiver  = receiver
    text_subtype = 'plain'

    try:
        msg = MIMEText(message, text_subtype)
        msg['Subject']= subject
        msg['From']   = sender
        msg['To']     = ', '.join(receiver)
        receiver = receiver + des_ccc 

        conn = SMTP(SMTPserver,587,l_hostname)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, receiver, msg.as_string())
        finally:
            conn.close()

    except Exception, exc:
        log( "mail failed; %s" % str(exc) ) # give a error message




def clean_files(BackupDir, DaysToKeep):
    now = time.time()
    filelist = [ f for f in os.listdir(BackupDir) if f.endswith(".gz") ]
    for f in filelist:
        f = os.path.join(BackupDir, f)
        if os.stat(f).st_mtime < now - (DaysToKeep * 86400):
            if os.path.isfile(f):
                os.remove(f)
                log('APAGANDO O ARQUIVO: %s COM MAIS DE %s DIAS ...' %(f, DaysToKeep))



def main():
    global verbose, message
    usage = "usage: %prog --backup [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("--host", action="store", type="string", dest="HOST", default=host_mysql, help="Entre com o IP do Mysql")
    parser.add_option("--user", action="store", type="string", dest="USER", default=user_mysql, help="Username do Mysql")
    parser.add_option("--passwd", action="store", type="string", dest="PASS", default=pass_mysql, help="Password do Mysql")
    parser.add_option("--clean", action="store", type="int", dest="CLEAN", default=False, help="Para limpar os arquivos X dias")
    parser.add_option("--backup", action="store_true", dest="BACKUP", default=False, help="Para fazer Backup")
    parser.add_option("--debug", action="store_true", dest="DEBUG", default=False, help="Para habilitar Debug")
    parser.add_option("--sendmail", action="store_true", dest="SENDMAIL", default=False, help="Para enviar E-mail")
    options, args = parser.parse_args()
    

    if (options.DEBUG): verbose = True

    if (options.BACKUP):
        log("[***JOB DE BACKUP MYSQL****]")
        exec_backup(backup_dir)
        check_mysql()
        if (options.CLEAN): clean_files(backup_dir, options.CLEAN)
        if (options.SENDMAIL): send_mail(destination, "LOG BACKUP MYSQL")
        salve_log = open(log_file,"w"); salve_log.write(message); salve_log.close()


if __name__ == "__main__":
    main()