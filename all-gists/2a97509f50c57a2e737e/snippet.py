#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -*- coding: utf-8 -*-
#
# Wordpress Watcher
# Automating WPscan to scan and report vulnerable Wordpress sites
# Florian Roth
# v0.1
# March 2015
#
# DISCLAIMER - USE AT YOUR OWN RISK.

import os
import re
import smtplib
import traceback
from subprocess import check_output, CalledProcessError, STDOUT
from email.mime.text import MIMEText
from datetime import datetime

# General Options
wpscan_dir              = r'/root/wpscan'
wp_sites                = [ 'www.site1.de', 'www.site2.de' ]
false_positive_strings  = [ 'XML-RPC', 'GHOST vulnerability' ]

# Log file
log_file                = r'./wpwatcher.log'

# Email Report
send_email_report       = True
smtp_server             = r'smtp.server.net:587' # 'server:port'
smtp_auth               = True
smtp_user               = 'office'
smtp_pass               = 'pass'
smtp_ssl                = True
to_email                = r'myemail@gmail.com'
from_email              = r'wpwatcher@work.net'


# Check if WPScan is installed
def is_wpscan_installed():

    if not os.path.exists(wpscan_dir):
        result = check_output(r'mkdir -p %s' % wpscan_dir, shell=True)
        if result:
            print "[ERROR] %s" % result.replace("\n", " ")
            sys.exit(1)
        return 0
    else:
        return 1


# Install WPScan from github
# This function is likely to fail as it strongly depends ton the OS platform
# and other settings to succeed
# I strongly recommend installing WPScan yourself and set the directory in the
# options above
def install_wpscan():
    print "[INFO] Trying to install WPScan"
    os.chdir(wpscan_dir)
    try:
        result = check_output(r'GIT_CURLOPT_SSLVERSION=3 && git clone https://github.com/wpscanteam/wpscan.git && gem install bundler && bundle install --without test', stderr=STDOUT, shell=True, universal_newlines=True)
    except CalledProcessError as exc:
        print "[ERROR]", exc.returncode, exc.output
        print "If errors occur - try to install wpscan and all dependancies manually"
    print "[INFO] %s" % result


# Update WPScan from github
def update_wpscan():
    print "[INFO] Updating WPScan"
    os.chdir(wpscan_dir)
    try:
        result = check_output(r'./wpscan.rb --batch --update', stderr=STDOUT, shell=True, universal_newlines=True)
    except CalledProcessError as exc:
        print "[ERROR]", exc.returncode, exc.output
    print result


# Run WPScan on defined domains
def run_scan():
    print "[INFO] Starting scans on configured sites"
    os.chdir(wpscan_dir)
    for wp_site in wp_sites:

        # Scan ----------------------------------------------------------------
        try:
            print "[INFO] Scanning '%s'" % wp_site
            result = check_output(r'./wpscan.rb --batch --url %s' % wp_site, stderr=STDOUT, shell=True, universal_newlines=True)
        except CalledProcessError as exc:
            print "[ERROR]", exc.returncode, exc.output

        # Parse the results ---------------------------------------------------
        (warnings, alerts) = parse_results(result)

        # Report Options ------------------------------------------------------
        # Email
        if send_email_report:
            send_report(wp_site, warnings, alerts)
        # Logfile
        try:
            with open(log_file, 'a') as log:
                for warning in warnings:
                    log.write("%s %s WARNING: %s\n" % (get_timestamp(), wp_site, warning))
                for alert in alerts:
                    log.write("%s %s ALERT: %s\n" % (get_timestamp(), wp_site, alert))
        except Exception, e:
            traceback.print_exc()
            print "[ERROR] Cannot write to log file"


# Parsing the results
def parse_results(results):

    warnings = []
    alerts = []
    warning_on = False
    alert_on = False
    last_message = ""

    # Parse the lines
    for line in results.splitlines():

        # Remove colorization
        line = re.sub(r'(\x1b|\[[0-9][0-9]?m)','',line)

        # Empty line = end of message
        if line == "" or line.startswith("[+]"):
            if warning_on:
                if not is_false_positive(warning):
                    warnings.append(warning)
                warning_on = False
            if alert_on:
                if not is_false_positive(alert):
                    alerts.append(alert)
                alert_on = False

        # Add to warning/alert
        if warning_on:
            warning += " / %s" % line.lstrip(" ")
        if alert_on:
            alert += " / %s" % line.lstrip(" ")

        # Start Warning/Alert
        if line.startswith("[i]"):
            # Warning message
            warning = "%s / %s" % ( last_message, line )
            warning_on = True
        if line.startswith("[!]"):
            # Warning message
            alert = line
            alert_on = True

        # Store lase message
        last_message = line

    return ( warnings, alerts )


# Send email report
def send_report(wp_site, warnings, alerts):

    print "[INFO] Sending email report stating items found on %s to %s" % (wp_site, to_email)

    try:
        message = "Issues have been detected by WPScan on one of your sites\n"

        if warnings:
            message += "\nWarnings\n"
            message += "\n".join(warnings)

        if alerts:
            message += "\nAlerts\n"
            message += "\n".join(alerts)

        mime_msg = MIMEText(message)

        mime_msg['Subject'] = 'WPWatcher report on %s - %s' % (wp_site, get_timestamp())
        mime_msg['From'] = from_email
        mime_msg['To'] = to_email

        # SMTP Connection
        s = smtplib.SMTP(smtp_server)
        s.ehlo()
        # SSL
        if smtp_ssl:
            s.starttls()
        # SMTP Auth
        if smtp_auth:
            s.login(smtp_user, smtp_pass)
        # Send Email
        s.sendmail(from_email, to_email, mime_msg.as_string())
        s.quit()

    except Exception, e:
        traceback.print_exc()


# Is the line defined as false positive
def is_false_positive(string):
    # False Positive Detection
    for fp_string in false_positive_strings:
        if fp_string in string:
            # print fp_string, string
            return 1
    return 0


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':

    # Check if WP-Scan exists
    if not is_wpscan_installed():
        install_wpscan()
    else:
        update_wpscan()

    # Run Scan
    run_scan()
