import subprocess
import argparse
import re
import sys
import requests

def do_dig(domain):
    command = "dig {} | grep IN".format(domain)
    try:
        output = subprocess.check_output(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        return re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", output)
    except:
        return []

def do_nslookup(ip):
    command = "nslookup {}".format(ip)
    try:
        output = subprocess.check_output(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        return output.split('name =')[1].split('\n')[0][1:-1]
    except:
        return None

def look_up(domain):
    ip_candidates = do_dig(domain)
    for ip in ip_candidates:
        res = do_nslookup(ip)
        if res and 'amazonaws.com' in res and 's3' in res:
            region = res.replace(domain, '').split('.')[0].replace('s3-website-', '')
            tmp_domain = "{}.s3.amazonaws.com".format(domain)
            req = requests.get("http://{}".format(tmp_domain))
            print "[!] {} === {}.{}".format(domain, domain, res)
            print "[!] Check: aws s3 ls s3://{}/ --no-sign-request --region {}".format(domain, region)
            print "[!] Check: {} in your browser, status_code: {}".format(tmp_domain, req.status_code)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AWS Scan')
    parser.add_argument('-d', action="store", dest="domain", default=None, help="Domain to look for (eg. flaws.cloud)")
    parser.add_argument('-f', action="store", dest="file", default=None, help="File to load (eg. domains.txt)")
    params = parser.parse_args()

    if not params.file and not params.domain:
        parser.print_help()
        sys.exit(-1)

    domains = []
    # domain parameter
    if params.domain:
        domains.append(params.domain)
    # file parameter
    if params.file:
        with open(params.file) as f:
            lines = f.readlines()
            for line in lines:
                domains.append(line.rstrip())

    for domain in domains:
        look_up(domain)