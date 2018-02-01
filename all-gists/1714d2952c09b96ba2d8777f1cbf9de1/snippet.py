import requests
import json
import pprint
import sys
import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
import dns.reversename
import time
from bs4 import BeautifulSoup
import multiprocessing
import optparse
from tabulate import tabulate

noOfThreads=1
domain=''

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

def retrieve_txt_record(table):
    res = []
    for td in table.findAll('td'):
        res.append(td.text)
    return res

def retrieve_results(table):
    res = []
    trs = table.findAll('tr')
    for tr in trs:
        tds = tr.findAll('td')
        tmpdomain = ((str(tds[0]).split("https://api.hackertarget.com/httpheaders/?q=http://")[1]).split('"><span class="glyphicon glyphicon-globe"')[0]).strip()
        if len(tmpdomain)>0:
	        res.append(tmpdomain)
    return res

def getSubdomains(domain):
	tmpResultList=[]
	dnsdumpster_url = 'https://dnsdumpster.com/'
	s = requests.session()
	req = s.get(dnsdumpster_url)
	soup = BeautifulSoup(req.content,"lxml")
	csrf_middleware = soup.findAll('input', attrs={'name': 'csrfmiddlewaretoken'})[0]['value']

	cookies = {'csrftoken': csrf_middleware}
	headers = {'Referer': dnsdumpster_url}
	data = {'csrfmiddlewaretoken': csrf_middleware, 'targetip': domain}
	req = s.post(dnsdumpster_url, cookies=cookies, data=data, headers=headers)

	if req.status_code != 200:
	    print sys.stderr
	soup = BeautifulSoup(req.content,"lxml")
	tables = soup.findAll('table')
	res = {}
	res['domain'] = domain
	res['dns_records'] = {}
	try:
		res['dns_records']['host'] = retrieve_results(tables[3])
		for x in res['dns_records']['host']:
			tmpResultList.append(x)
	except IndexError:
		pass
	return tmpResultList
def resolveDNS(tmpdomainName):
	resultList=[]	
	complete=False
	while complete==False:
		myResolver = dns.resolver.Resolver() 
		try:
			myAnswers = myResolver.query(tmpdomainName, "A")
			for rdata in myAnswers:
				resultList.append(str(rdata.to_text()))
		except dns.resolver.NoAnswer as e:
			pass
		except dns.resolver.NXDOMAIN as e:
			pass
		except dns.resolver.NoNameservers as e:
			pass
		except dns.exception.Timeout:
			#print "- DNS Timeout - Retry: "+str(tmpdomainName)
			time.sleep(5)
		complete=True
	return tmpdomainName,resultList

def getHTML(url):
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; rv:30.0) Gecko/20150101 Firefox/32.0", 
				"Connection": "keep-alive"
				}
	r = requests.get(url, headers=headers, verify=False, timeout=15,allow_redirects=False)
	html_content = r.text
	return html_content

parser = optparse.OptionParser()
parser.add_option('-t', action="store", dest="threads", help="number of threads")
parser.add_option('-n', action="store", dest="domain", help="domain name")
parser.add_option('-r', action="store_true", help="resolve DNS name")
parser.add_option('-s', action="store_true", help="find subdomains")
options, remainder = parser.parse_args()

if options.threads:
	noOfThreads=int(options.threads)
if options.domain:
	domain=options.domain
else:
	print "[*] Please enter a domain name"
	sys.exit()

url='https://app.securitytrails.com/api/whois/history/'+domain
html_content=getHTML(url)
data = json.loads(html_content)
organizationNameList=[]
if "API rate limit exceeded" in str(data):
	print "[*] API limit exceeded. Please try with another IP address"
	sys.exit()
else:
	for x in data['result']['items']:
		try:
			if x['contact'][0]['organization'] not in organizationNameList:
				organizationNameList.append(x['contact'][0]['organization'])
		except KeyError:
			pass
		except IndexError:
			pass
		'''
		try:
			if x['contact'][0]['name'] not in organizationNameList:
				organizationNameList.append(x['contact'][0]['name'])
		except KeyError:
			pass
		'''
	if len(organizationNameList)>0:
		print "[*] Found the below organization names"
		print ", ".join(organizationNameList)

		dnsList=[]
		print "\n[*] Found the below domains"
		for x in organizationNameList:
			x=x.replace(" ","%20")
			count=0
			while count<200:
				newUrl='https://app.securitytrails.com/api/whois/list/organization/'+x+'?page='+str(count)
				html_content=getHTML(newUrl)
				data = json.loads(html_content)
				#print newUrl
				if data['success']==True:
					if data['result']!='Elasticsearch request failed':
						#print len(data['result'])
						if len(data['result'])>0:
							for y in data['result']:
								#tmpResultList=resolveDNS(y)
								#if len(tmpResultList)<1:
								if y not in dnsList:
									print y
									dnsList.append(y)
						else:
								count=201
								#sys.exit()
				count+=1
		tmpResultList1=[]
		if options.r:
			p = multiprocessing.Pool(processes=noOfThreads)
			tmpResultList = p.map(resolveDNS,dnsList)		
			p.close()
			for x in tmpResultList:
				tmpDomainName=x[0]
				tmpHostList=", ".join(x[1])
				tmpResultList1.append([tmpDomainName,tmpHostList])
			print "\n[*] Domain Results"
			print tabulate(tmpResultList1)
		tmpResultList2=[]
		if options.s:
			for x in tmpResultList1:
				tmpSubdomainList=getSubdomains(str(x[0]))
				for y in tmpSubdomainList:
					tmpResultList2.append(y)
			p = multiprocessing.Pool(processes=noOfThreads)
			tmpResultList = p.map(resolveDNS,tmpResultList2)		
			p.close()
			tmpResultList1=[]
			if len(tmpResultList)>0:
				for x in tmpResultList:
					tmpDomainName=x[0]
					tmpHostList=", ".join(x[1])
					tmpResultList1.append([tmpDomainName,tmpHostList])				
				print "\n[*] Subdomain Results"
				print tabulate(tmpResultList1)
	else:
		print "\n[*] No organizations found. Please enter another domain name"