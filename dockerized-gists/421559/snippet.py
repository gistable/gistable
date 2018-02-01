#!/usr/bin/env python

"""
A script to query the Amazon Web Services usage reports programmatically.

Ideally this wouldn't exist, and Amazon would provide an API we can use 
instead, but hey - that's life.

Basically takes your AWS account username and password, logs into the
website as you, and grabs the data out. Always gets the 'All Usage Types'
report for the specified service.

Requirements: 

* Mechanize: http://wwwsearch.sourceforge.net/mechanize/
  You can install this via pip/easy_install

Run with -h to see the available options.
"""

import os
import sys
from datetime import date
import time

import mechanize

FORMATS = ('xml', 'csv')
PERIODS = ('hours', 'days', 'months')
SERVICES = ('AmazonS3', 'AmazonEC2', 'AmazonCloudFront', 'AmazonSimpleDB', 'AWSQueueService', 'IngestionService', 'AmazonVPC',)

FORM_URL = "https://aws-portal.amazon.com/gp/aws/developer/account/index.html?ie=UTF8&action=usage-report"

def get_report(service, date_from, date_to, username, password, format='csv', period='days', debug=False):
    br = mechanize.Browser()
    br.set_handle_robots(False)

    if debug:
        # Log information about HTTP redirects and Refreshes.
        br.set_debug_redirects(True)
        # Log HTTP response bodies (ie. the HTML, most of the time).
        br.set_debug_responses(True)
        # Print HTTP headers.
        br.set_debug_http(True)
    
    br.addheaders = [
        # the login process 404s if you leave Python's UA string
        ('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1) Gecko/20090701 Ubuntu/9.04 (jaunty) Firefox/3.5'),
        ('Accept', 'text/html, application/xml, */*'),
    ]
    
    # login
    print >>sys.stderr, "Logging in..."
    try:
        resp = br.open(FORM_URL)
        br.select_form(name="signIn")
        br["email"] = username
        br["password"] = password
        resp = br.submit()  # submit current form
    except Exception, e:
        print >>sys.stderr, "Error logging in to AWS"
        raise
    
    # service selector
    print >>sys.stderr, "Selecting service %s..." % service
    br.select_form(name="usageReportForm")
    br["productCode"] = [service]
    resp = br.submit()
    
    # report selector
    print >>sys.stderr, "Building report..."
    br.select_form(name="usageReportForm")
    br["timePeriod"] = ["Custom date range"]
    br["startYear"] = [str(date_from.year)]
    br["startMonth"] = [str(date_from.month)]
    br["startDay"] = [str(date_from.day)]
    br["endYear"] = [str(date_to.year)]
    br["endMonth"] = [str(date_to.month)]
    br["endDay"] = [str(date_to.day)]
    br["periodType"] = [period]
    
    resp = br.submit("download-usage-report-%s" % format)
    return resp.read()
    
if __name__ == "__main__":
    from optparse import OptionParser
    
    USAGE = (
        "Usage: %prog [options] -s SERVICE DATE_FROM DATE_TO\n\n"
        "DATE_FROM and DATE_TO should be in YYYY-MM-DD format (eg. 2009-01-31)\n"
        "Username and Password can also be specified via AWS_USERNAME and AWS_PASSWORD environment variables.\n"
        "\n"
        "Available Services: " + ', '.join(SERVICES)
    )
    parser = OptionParser(usage=USAGE)
    parser.add_option('-s', '--service', dest="service", type="choice", choices=SERVICES, help="The AWS service to query")
    parser.add_option('-p', '--period', dest="period", type="choice", choices=PERIODS, default='days', metavar="PERIOD", help="Period of report entries")
    parser.add_option('-f', '--format', dest="format", type="choice", choices=FORMATS, default='csv', metavar="FORMAT", help="Format of report")
    parser.add_option('-U', '--username', dest="username", metavar="USERNAME", help="Email address for your AWS account")
    parser.add_option('-P', '--password', dest="password", metavar="PASSWORD")
    parser.add_option('-d', '--debug', action="store_true", dest="debug", default=False)
    
    opts, args = parser.parse_args()
    if len(args) < 2:
        parser.error("Missing date range")
    date_range = [date(*time.strptime(args[i], '%Y-%m-%d')[0:3]) for i in range(2)]
    if date_range[1] < date_range[0]:
        parser.error("End date < start date")
    
    if not opts.service:
        parser.error("Specify a service to query!")
    
    if not opts.username and not os.environ.get('AWS_USERNAME'):
        parser.error("Must specify username option or set AWS_USERNAME")
    if not opts.password and not os.environ.get('AWS_PASSWORD'):
        parser.error("Must specify password option or set AWS_PASSWORD")
    
    kwopts = {
        'service': opts.service,
        'date_from': date_range[0],
        'date_to': date_range[1],
        'format': opts.format,
        'period': opts.period,
        'username': opts.username or os.environ.get('AWS_USERNAME'),
        'password': opts.password or os.environ.get('AWS_PASSWORD'),
        'debug': opts.debug,
    }
    
    print get_report(**kwopts)
