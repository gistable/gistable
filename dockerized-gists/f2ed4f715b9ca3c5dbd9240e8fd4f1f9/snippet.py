#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright ©2017-01-16 Alex <vitrun@gmail.com>
#
"""
crawl the itjuzi.com company data
"""
import requests
import time
import sys

class Scraper(object):
    """itjuzi scraper"""
    def __init__(self, cookie_str, auth_str):
        self.cookie_str = cookie_str
        self.auth_str = auth_str

    def _make_headers(self):
        return {
            'Host': 'cobra.itjuzi.com',
            'Cookie': self.cookie_str,
            'userid': 0,
            'User-Agent': 'v4_itjuzi/3.7.5 (iPhone; iOS 10.1.1; Scale/2.00)',
            'Authorization': self.auth_str,
        }

    def _curl(self, url, headers=None):
        for i in range(0, 3):
            try:
                res = requests.get(url, headers=headers)
                if res.ok:
                    return res.json()
            except Exception, e:
                if i == 3:
                    print e
        return None

    def curl_company_list(self, page):
        api = 'https://cobra.itjuzi.com/api/company?com_all=1&page=%d' % page
        return self._curl(api, self._make_headers())

    def curl_company_detail(self, id):
        api = 'https://cobra.itjuzi.com/api/company/%d' % id
        return self._curl(api, self._make_headers())

    def _get_company_info_tiny(self, docs):
        coms = []
        for doc in docs:
            scope = doc.get('company_scope', [])
            sub_scope = doc.get('company_sub_scope', [])
            scopes = []
            for i in range(min(len(scope), len(sub_scope))):
                scopes.append('%s-%s' % (scope[i]['cat_name'], sub_scope[i]['cat_name']))
            tags = [v['tag_name'] for v in doc.get('company_tag', [])]
            invest = doc.get('company_invest_events', [])
            invest_desc = invest and '%s: %s%s' % (
                invest[0]['invse_round']['invse_round_name'],
                invest[0]['invse_currency']['invse_currency_num'],
                invest[0]['invse_currency']['invse_currency_name'],
                )
            persons = doc.get('company_with_per', [])
            person_descs = ['%s:%s' % (v['des'], v['per_name']) for v in persons]

            coms.append({
                'name': doc.get('com_name'),
                'juzi_home': 'http://www.itjuzi.com/company/%s' % doc.get('com_id'),
                'desc': doc.get('com_des'),
                'location': '%s%s' % (doc.get('com_prov', ''),
                    doc.get('com_city', '')),
                'birth': '%d-%d' % (doc.get('com_born_year', 0),
                        doc.get('com_born_month', 0)),
                'fund': doc.get('com_fund', {}).get('com_fund_status_name'),
                'scope': ' '.join(scopes),
                'company': doc.get('com_registered_name'),
                'url': doc.get('com_url'),
                'addr': doc.get('com_cont_addr'),
                'email': doc.get('com_cont_email'),
                'tel': doc.get('com_cont_tel_hide'),
                'status': doc.get('company_status', {}).get('com_status_name'),
                'tags': ' '.join(tags),
                'invest': invest_desc,
                'person': ' '.join(person_descs)
            })
        return coms

    def _print_csv(self, docs, fout):
        for doc in docs:
            vals = [('"%s"' % (v or '')).encode('utf8').replace(',', '，')
                for v in doc.values()]
            print >> fout, ','.join([str(i) for i in vals])
        fout.flush()

    def curl_all_companies(self, start_page=1, out_file=None):
        doc = self.curl_company_list(1)
        companies = []
        fout = out_file and open(out_file, 'a')
        for i in range(start_page, doc['last_page']+1):
            doc = self.curl_company_list(i)
            if doc:
                coms = doc['data']
                for com in coms:
                    detail_doc = self.curl_company_detail(com['com_id'])
                    com.update(detail_doc)
                companies.extend(coms)
                if fout:
                    tiny_docs = self._get_company_info_tiny(coms)
                    self._print_csv(tiny_docs, fout)
            print 'curling page ', i
            time.sleep(2)
        return companies


if __name__ == '__main__':
    print 'demo:'
    print "python crawl.py 1 com.csv acw_tc=AQAAANJhVTdDfgUAUavidBjTfxYTygRB 'Bearer b5zVf72QkxRBpN4tuAqeohkY2Q3sVNtI3xnkVMmp'"
    print ''
    scraper = Scraper(sys.argv[3], sys.argv[4])
    coms = scraper.curl_all_companies(int(sys.argv[1]), sys.argv[2])