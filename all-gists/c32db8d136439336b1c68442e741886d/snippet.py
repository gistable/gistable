# coding=utf-8
# Note:
#     1. 使用Redis缓存用户信息，减少重复调用
#     2. 只通过用户的location字段看是否包含beijing、shanghai、guangzhou、
#        shenzhen、china这几个关键词判断是否是国人
from collections import defaultdict
import redis
import requests

USENAME = '<YOUR USERNSME>'
PASSWRD = '<YOUR PASSWORD>'
LOCATIONS = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'china']
REPOS = ['pallets/flask', 'django/django', 'kennethreitz/requests',
         'rg3/youtube-dl', 'ansible/ansible', 'pypa/virtualenv',
         'pypa/pip', 'zzzeek/sqlalchemy', 'MongoEngine/mongoengine',
         'tomchristie/django-rest-framework', 'pallets/jinja', 'celery/celery',
         'nvie/rq', 'wtforms/wtforms', 'getpelican/pelican', 'saltstack/salt',
         'benoitc/gunicorn', 'pallets/werkzeug', 'getsentry/sentry',
         'pytest-dev/pytest', 'cython/cython', 'docker/compose',
         'docker/docker-py', 'pydata/pandas', 'andymccurdy/redis-py',
         'ipython/ipython', 'fabric/fabric', 'jkbrzt/httpie', 'scrapy/scrapy',
         'tornadoweb/tornado', 'python/cpython']
API_URL = 'https://api.github.com'
LOCATION_KEY = 'location:{}'
CONTRIBUTOR_MAP = defaultdict(list)
ROW_FORMAT = '{:<21}\t{:<8}\t{}'


s = requests.Session()
s.auth = (USENAME, PASSWRD)
conn = redis.Redis()


def is_cn_contributor(username):
    key = LOCATION_KEY.format(username)
    location = conn.get(key)
    if not location:
        r = s.get('https://api.github.com/users/{}'.format(username))
        location = r.json()['location']
        conn.set(key, location)
    if location is not None and any([loc in location.lower() for loc in LOCATIONS]):
        return True
    return False


def get_repo_contributors(repo):
    all_contributors = 0
    cn_contributors = 0
    page = 1

    while 1:
        r = s.get('{}/repos/{}/contributors?page={}'.format(API_URL, repo, page))
        contributors = r.json()
        if not contributors:
            break
        all_contributors += len(contributors)

        for contributor in contributors:
            username = contributor['login']
            if is_cn_contributor(username):
                cn_contributors += 1
                CONTRIBUTOR_MAP[username].append(repo)

        page += 1

    return repo.split('/')[1], all_contributors, cn_contributors


def get_cn_creator_by_search():
    page = 1
    creator_lst = []

    while 1:
        r = s.get(('{}/search/repositories?q=language:python&sort=stars'
                   '&order=desc&page={}').format(API_URL, page))
        if 'Link' not in r.headers:
            break
        repos = r.json()['items']
        for repo in repos:
            username = repo['owner']['login']
            if is_cn_contributor(username):
                creator_lst.append((
                    repo['full_name'],
                    username,
                    repo['stargazers_count']
                ))
        page += 1
    return creator_lst


def tabulate(header, data, row_format=ROW_FORMAT):
    print '-' * 79
    for row in [header] + data:
        print row_format.format(*row)
        
        
def main():
    contributor_lst = [get_repo_contributors(repo)
                       for repo in REPOS]
    tabulate(
        ['项目', '总贡献者', '中国贡献者'],
        contributor_lst
    )

    contributor_lst = []

    for username, repos in sorted(CONTRIBUTOR_MAP.items(),
                                  key=lambda k: len(k[1]),
                                  reverse=True)[:20]:
        contributor_lst.append((
            username, len(repos),
            ' '.join(repo.split('/')[1] for repo in repos)
        ))
    tabulate(
        ['ID', '贡献次数', '项目列表'],
        contributor_lst
    )

    creators = get_cn_creator_by_search()
    tabulate(
        ['项目', '创建者', 'Star数'],
        creators,
        '{:<30}\t{:<12}\t{}'
    )


if __name__ == '__main__':
    main()