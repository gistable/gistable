#!/usr/bin/python

from locust import HttpLocust, TaskSet, task
import random

terms = [
    'chemistry', 'physics', 'biology', 'computer science',
    'web of science', 'google scholar', 'refworks', 'pubmed',
    'ieee', 'jstor', 'scifinder', 'morningstar', 'petition',
    'citation builder', 'nature', 'science', 'proquest', 'naxos',
    'printing', 'study room', '3d printing', 'Fishing in contested waters',
    'Pirate fishing elimination act report of the committee'
]

class UserBehavior(TaskSet):

    @task(1)
    def index(l):
        l.client.get('/')

    @task(3)
    def search(l):
        global terms
        l.client.get('/?q=%s' % random.choice(terms), name='/?q=[query]')

    @task(2)
    def website_search(l):
        global terms
        l.client.get('/website/?q=%s' % random.choice(terms),
            name='/website/?q=[query]')

    @task(2)
    def best_bets_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=best_bets&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Best Bets XHR Endpoint')

    @task(2)
    def summon_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=summon&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Summon XHR Endpoint')

    @task(2)
    def catalog_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=catalog&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Catalog XHR Endpoint')

    @task(2)
    def ematrix_journal_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=ematrix_journal&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Ematrix Journal XHR Endpoint')

    @task(2)
    def ematrix_database_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=ematrix_database&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Ematrix Database XHR Endpoint')

    @task(2)
    def faq_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=faq&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='FAQ XHR Endpoint')

    @task(2)
    def smart_subjects_endpoint_search(l):
        global terms
        l.client.get('/xhr_search/?endpoint=smart_subjects&page=1&template=without_paging&q=%s' % random.choice(terms),
            name='Smart Subjects XHR Endpoint')


class QuicksearchUser(HttpLocust):
    task_set = UserBehavior
    min_wait=1000
    max_wait=5000
