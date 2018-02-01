#!/usr/bin/python
import subprocess, sys, os.path, argparse
viewheader = True
verbose = True

parser = argparse.ArgumentParser(description='HTTP Security Header Tester: Joshua Platz')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-i', '--input', help='Input URL or URL input file name', required=True)
args=parser.parse_args()
sitesfile=args.input
xssprot=[]
xframe=[]
content=[]
keypin=[]
xcontent=[]
referrer=[]
sts=[]

def scanurl(site):
        out = str(subprocess.check_output(['curl', '-s', '-I', '--insecure', '-H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36"', site], timeout=10))
        if viewheader:
                print ("----------------------------------------------------------------------")
                print ("The original request was: " +str(site))
                print ("----------------------------------------------------------------------")
                print (out)
                print ("----------------------------------------------------------------------")
        #Check For - X-XSS-Protection
        if "X-XSS-Protection" in str(out):
                if verbose:
                        print ("X-XSS-Protection Enabled!" + str(site))
        else:
                xssprot.append(str(site))
                if verbose:
                        print ("X-XSS-Protection Not Detected on: " +str(site))
        #Check For - X-Frame-Options
        if "X-Frame-Options" in str(out):
                if verbose:
                        print ("X-Frame-Options Enabled!" + str(site))
        else:
                xframe.append(str(site))
                if verbose:
                        print ("X-Frame-Options Not Detected on: " +str(site))
        #Check For - Content-Security-Policy
        if "Content-Security-Policy" in str(out):
                if verbose:
                        print ("Content-Security-Policy Enabled!" + str(site))
        else:
                content.append(str(site))
                if verbose:
                        print ("Content-Security-Policy Not Detected on: " +str(site))
        #Check For - Public-Key-Pins
        if "Public-Key-Pins" in str(out):
                if verbose:
                        print ("Public-Key-Pins Enabled!" + str(site))
        else:
                keypin.append(str(site))
                if verbose:
                        print ("Public-Key-Pins Not Detected on: " +str(site))
        #Check For - X-Content-Type-Options
        if "X-Content-Type-Options" in str(out):
                if verbose:
                        print ("X-Content-Type-Options Enabled!" + str(site))
        else:
                xcontent.append(str(site))
                if verbose:
                        print ("X-Content-Type-Options Not Detected on: " +str(site))
        #Check For - Referrer-Policy
        if "Referrer-Policy" in str(out):
                if verbose:
                        print ("Referrer-Policy Enabled!" + str(site))
        else:
                referrer.append(str(site))
                if verbose:
                        print ("Referrer-Policy Not Detected on: " +str(site))
        #Check For - Strict-Transport-Security
        if "Strict-Transport-Security" in str(out):
                if verbose:
                        print ("Strict-Transport-Security Enabled!" + str(site))
        else:
                sts.append(str(site))
                if verbose:
                        print ("Strict-Transport-Security Not Detected on: " +str(site))
        
        if viewheader:
                print ("----------------------------------------------------------------------")

if os.path.isfile(sitesfile):
        f = open(sitesfile,'r')
        sites=f.readlines()
        for site in sites:
                try:
                        scanurl(site.rstrip('\r\n'))
                except:
                        print ("Error connecting to: " + str(site).rstrip('\r\n'))
        f.close

if not os.path.isfile(sitesfile):
        site=args.input
        scanurl(site)

if xssprot:
        print ("The following systems were missing the X-XSS-Protection Header: ")
        print (xssprot)
if xframe:
        print ("The following systems were missing the X-Frame-Options Header: ")
        print (xframe)
if content:
        print ("The following systems were missing the Content-Security-Policy Header: ")
        print (content)
if keypin:
        print ("The following systems were missing the Public-Key-Pins Header: ")
        print (keypin)
if xcontent:
        print ("The following systems were missing the X-Content-Type-Options Header: ")
        print (xcontent)
if referrer:
        print ("The following systems were missing the Referrer-Policy Header: ")
        print (referrer)
if sts:
        print ("The following systems were missing the Strict-Transport-Security Header: ")
        print (sts)
