#!/usr/bin/python
# Public domain
import wikitools

username = 'Legoktm'
password = 'hunter2'
messages = ['Signupstart', 'Signupend']
reason = '...'

def matrix(wiki):
    params = {
        'action': 'sitematrix',
        'format': 'json',
    }
    req = wikitools.api.APIRequest(wiki, params)
    data = req.query()
    for val in data['sitematrix']:
        if val.isdigit():
            for site in data['sitematrix'][val]:
                yield wikitools.Wiki(site['url'])
        elif val == 'specials':
            for site in data['sitematrix'][val]:
                if not 'private' in site:  # Let someone else touch these...
                    yield wikitools.Wiki(site['url'])

def do_wiki(wiki):
    wiki.login(username, password)
    for msg in messages:
        pg = wikitools.Page(wiki, 'MediaWiki:' + msg)
        if pg.exists:
            pg.edit(text='', summary=reason)

def main():
    meta = wikitools.Wiki('https://meta.wikimedia.org/w/api.php')
    for wiki in matrix(meta):
        do_wiki(wiki)
    

if __name__ == '__main__':
    main()