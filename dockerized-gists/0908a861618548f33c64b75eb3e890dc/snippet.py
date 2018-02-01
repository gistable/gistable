"""
Extract/export issue to csv 
MIT License
Copyright (c) [2016] [Jingo Rodriguez]
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import csv
import requests

'''
Variables need to be modify
'''
git_user    = ''
git_pass    = ''
git_repo    = '' #format use should be username/repo
extra_param = ''
git_auth    = (git_user,git_pass)

def write_to_csv(response):
	csvfile = '%s-issues.csv' % (git_repo.replace('/', '-'))
	csvout  = csv.writer(open(csvfile, 'wb'))
	csvout.writerow(('id', 'title', 'label', 'body', 'Created at'))
	for issue in r.json():
		csvout.writerow([issue['id'], issue['title'], issue['label'].encode('utf-8'), issue['body'].encode('utf-8'), issue['created_at'].encode('utf-8')])

r = requests.get('https://api.github.com/repos/%s/issues%s' % (git_repo,extra_param), auth=git_auth);
if r.status_code == 200:
	write_to_csv(r)
else:
	raise Exception(r.status_code)