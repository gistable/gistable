import json
import urllib
import urllib2
import xml.dom.minidom


# AC: OP
project_slugs = {
    'tu-munich': 'new-project',
}

ac_token = '<token-id>'
ac_url = 'https://url.active.colab.com/'
ac_api_url = ac_url + 'api.php'
ac_permalink_url = ac_url + 'projects/'

op_url = 'http://openproject.url/'
op_token = '<token-id>'
op_type_id = 3  # type id from url /types
op_status_id = 1  # /statuses
op_api_url = op_url + 'api/v2/'


"""
HTML <-> text conversions.
"""
from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint
import re


class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = unichr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(unichr(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))


def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except HTMLParseError:
        pass
    return parser.get_text()


def _filter(data, _set):
    return {key: data[key] for key in _set}


def ac_send_req(command, arguments=None, _format='json'):
    try:
        values = {
            'auth_api_token': ac_token,
            'path_info': command,
            'format': _format,
        }

        if arguments:
            values.update(arguments)

        data = urllib.urlencode(values)
        url_with_data = ac_api_url + "/?" + data
        req = urllib2.Request(url_with_data)
        response = urllib2.urlopen(req)
        the_page = response.read()

        if _format == 'json':
            return json.loads(the_page)
        return the_page
    except:
        print 'Error, trying again...'
        ac_send_req(command, arguments=arguments, _format=_format)


def ac_get_notebooks(pid):
    notebooks_xml = ac_send_req('projects/%d/notebooks' % pid, _format='xml')
    pxml = xml.dom.minidom.parseString(notebooks_xml)
    notebooks = []
    for notebook_xml in pxml.getElementsByTagName('notebook'):
        notebook = {
            'pages': [],
        }
        for item in ['id', 'name', 'permalink']:
            notebook[item] = notebook_xml.getElementsByTagName(
                item)[0].firstChild.nodeValue
        body_xml = notebook_xml.getElementsByTagName('body')
        if body_xml:
            notebook['body'] = body_xml[0].firstChild.nodeValue

        print '    Getting "%s" pages' % notebook['name']
        for page_xml in notebook_xml.getElementsByTagName('subpage'):
            link = page_xml.getElementsByTagName(
                'permalink')[0].firstChild.nodeValue
            page_id = int(link.split('/')[-1])
            page = ac_send_req(
                'projects/%d/notebooks/%d/pages/%d' % (
                    pid, int(notebook['id']), page_id)
            )
            npage = _filter(page, [
                'name',
                'body',
                'permalink',
            ])
            notebook['pages'].append(npage)
        notebooks.append(notebook)
    return notebooks


def ac_get_tasks(pid):
    tasks = ac_send_req('projects/%d/tasks' % pid)
    ntasks = []
    for task in tasks:
        ntask = _filter(task, [
            'task_id',
            'name',
            'permalink',
            'body',
            'is_completed',
            'created_on',
        ])
        ntask['created_on'] = ntask['created_on']['mysql']

        print '    Getting "%s" comments' % ntask['name']
        comments = ac_send_req('projects/%d/tasks/%d/comments' % (
            pid, ntask['task_id']))
        ncomments = []
        if comments:
            for comment in comments:
                ncomment = _filter(comment, [
                    'permalink',
                    'body',
                    'created_by',
                    'created_on',
                ])
                ncomment['created_by'] = ncomment['created_by']['display_name']
                ncomment['created_on'] = ncomment['created_on']['mysql']
                ncomments.append(ncomment)

        ntask['comments'] = ncomments
        ntasks.append(ntask)
    return ntasks


def ac_get_info():
    print 'Getting companies'
    companies = ac_send_req('people')
    print 'Getting projects'
    projects = ac_send_req('projects')

    project_urls = {ac_permalink_url + p: p for p in project_slugs.keys()}
    p2export = []
    for project in projects:
        if project['permalink'] in project_urls.keys():
            project['op_slug'] = project_slugs[
                project_urls[project['permalink']]]
            p2export.append(project)

    company_ids = [p['company_id'] for p in p2export]
    c2export = []
    for company in companies:
        if company['id'] in company_ids:
            c2export.append(company)

    combined_data = []
    for company in c2export:
        ncompany = _filter(company, [
            'id',
            'name',
            'note',
            'office_address',
            'office_fax',
            'office_homepage',
            'office_phone',
            'permalink',
        ])
        cid = ncompany['id']
        ncompany['projects'] = []
        for project in p2export:
            if project['company_id'] != cid:
                continue

            nproject = _filter(project, [
                'id',
                'name',
                'permalink',
                'created_on',
                'op_slug',
            ])
            nproject['name'] = nproject['name'].split(':')[-1].strip()
            nproject['created_on'] = nproject['created_on']['mysql']

            print 'Getting "%s" notebooks' % nproject['name']
            nproject['notebooks'] = ac_get_notebooks(nproject['id'])
            print 'Getting "%s" tasks' % nproject['name']
            nproject['tasks'] = ac_get_tasks(nproject['id'])

            ncompany['projects'].append(nproject)
        combined_data.append(ncompany)
    return combined_data


def op_send_req(command, arguments=None, _filter=None, method='POST',
                _format='json'):
    try:
        values = {
            'key': op_token,
        }

        if _filter:
            values.update(_filter)
        data = urllib.urlencode(values)

        if method == 'POST':
            url = op_api_url + command + '.' + _format + "?" + data
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/%s' % _format)
            response = urllib2.urlopen(req, json.dumps(arguments))
        elif method == 'GET':
            url_with_data = op_api_url + command + '.' + _format + "?" + data
            req = urllib2.Request(url_with_data)
            req.add_header('Content-Type', 'application/%s' % _format)
            response = urllib2.urlopen(req)

        the_page = response.read()

        if _format == 'json':
            return json.loads(the_page)
        return the_page
    except urllib2.URLError, e:
        if e.code != 401:  # it will trow 401 yet it will create the task
            op_send_req(
                command,
                arguments=arguments,
                _filter=_filter,
                method=method,
                _format=_format
            )


def op_push_info(data):
    for company in data:
        for project in company['projects']:
            print 'Pushin project "%s"' % project['name']
            for task in project['tasks']:
                print '    Pushin task "%s"' % task['name']
                body = html_to_text(task['body'])
                if task['comments']:
                    for comment in task['comments']:
                        body += '\n> [%s] %s: %s' % (
                            comment['created_on'],
                            comment['created_by'],
                            '\n> '.join(html_to_text(
                                comment['body']).split('\n')),
                        )
                body += '\nURL: %s' % task['permalink']
                op_send_req(
                    'projects/%s/planning_elements' % project['op_slug'],
                    arguments={
                        'subject': task['name'],
                        'description': body,
                        'start_date': task['created_on'].split()[0],
                        'type_id': op_type_id,
                        'status_id': op_status_id,
                    }
                )


if __name__ == "__main__":
    op_push_info(ac_get_info())