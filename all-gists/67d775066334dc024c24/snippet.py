import requests
from requests.auth import HTTPBasicAuth
import re
from StringIO import StringIO

JIRA_URL = 'https://your-jira-url.tld/'
JIRA_ACCOUNT = ('jira-username', 'jira-password')
# the JIRA project ID (short)
JIRA_PROJECT = 'PRO'
GITLAB_URL = 'http://your-gitlab-url.tld/'
# this is needed for importing attachments. The script will login to gitlab under the hood.
GITLAB_ACCOUNT = ('gitlab-username', 'gitlab-password')
# this token will be used whenever the API is invoked and
# the script will be unable to match the jira's author of the comment / attachment / issue
# this identity will be used instead.
GITLAB_TOKEN = 'get-this-token-from-your-profile'
# the project in gitlab that you are importing issues to.
GITLAB_PROJECT = 'namespaced/project/name'
# the numeric project ID. If you don't know it, the script will search for it
# based on the project name.
GITLAB_PROJECT_ID = None
# set this to false if JIRA / Gitlab is using self-signed certificate.
VERIFY_SSL_CERTIFICATE = False

# IMPORTANT !!!
# make sure that user (in gitlab) has access to the project you are trying to
# import into. Otherwise the API request will fail.
GITLAB_USER_TOKENS = {
    'jira-username': 'gitlab-private-token-for-this-user',
}

RE_TOKEN = "<meta content=\"(?P<token>.*)\" name=\"csrf-token\""

jira_issues = requests.get(
    JIRA_URL + 'rest/api/2/search?jql=project=%s+AND+resolution=Unresolved+ORDER+BY+priority+DESC&maxResults=10000' % JIRA_PROJECT,
    auth=HTTPBasicAuth(*JIRA_ACCOUNT),
    verify=VERIFY_SSL_CERTIFICATE,
    headers={'Content-Type': 'application/json'}
)


if not GITLAB_PROJECT_ID:
    # find out the ID of the project.
    for project in requests.get(
        GITLAB_URL + 'api/v3/projects',
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE
    ).json():
        if project['path_with_namespace'] == GITLAB_PROJECT:
            GITLAB_PROJECT_ID = project['id']
            break

if not GITLAB_PROJECT_ID:
    raise Exception("Unable to find %s in gitlab!" % GITLAB_PROJECT)

for issue in jira_issues.json()['issues']:

    reporter = issue['fields']['reporter']['name']

    gl_issue = requests.post(
        GITLAB_URL + 'api/v3/projects/%s/issues' % GITLAB_PROJECT_ID,
        headers={'PRIVATE-TOKEN': GITLAB_USER_TOKENS.get(reporter, GITLAB_TOKEN)},
        verify=VERIFY_SSL_CERTIFICATE,
        data={
            'title': issue['fields']['summary'],
            'description': issue['fields']['description']
        }
    ).json()['id']

    # get comments and attachments
    issue_info = requests.get(
        JIRA_URL + 'rest/api/2/issue/%s/?fields=attachment,comment' % issue['id'],
        auth=HTTPBasicAuth(*JIRA_ACCOUNT),
        verify=VERIFY_SSL_CERTIFICATE,
        headers={'Content-Type': 'application/json'}
    ).json()

    for comment in issue_info['fields']['comment']['comments']:
        author = comment['author']['name']

        note_add = requests.post(
            GITLAB_URL + 'api/v3/projects/%s/issues/%s/notes' % (GITLAB_PROJECT_ID, gl_issue),
            headers={'PRIVATE-TOKEN': GITLAB_USER_TOKENS.get(author, GITLAB_TOKEN)},
            verify=VERIFY_SSL_CERTIFICATE,
            data={
                'body': comment['body']
            }
        )

    if len(issue_info['fields']['attachment']):
        # !!! HACK !!! obtain a session to gitlab in order to get a secret csrftoken
        with requests.Session() as s:
            token = re.search(
                RE_TOKEN,
                s.get(
                    GITLAB_URL + 'users/sign_in',
                    verify=VERIFY_SSL_CERTIFICATE
                ).content
            ).group('token')

            signin = s.post(
                GITLAB_URL + 'users/sign_in',
                headers={
                    "Referer": GITLAB_URL
                },
                verify=VERIFY_SSL_CERTIFICATE,
                data={
                    'authenticity_token': token,
                    'user[login]': GITLAB_ACCOUNT[0],
                    'user[password]': GITLAB_ACCOUNT[1],
                    'user[remember_me]': 0
                }
            )

            html = s.get(
                GITLAB_URL + '%s/issues/%s' % (GITLAB_PROJECT, gl_issue),
                verify=VERIFY_SSL_CERTIFICATE
            ).content

            token = re.search(RE_TOKEN, html).group('token')

            for attachment in issue_info['fields']['attachment']:
                author = attachment['author']['name']

                _file = requests.get(
                    attachment['content'],
                    auth=HTTPBasicAuth(*JIRA_ACCOUNT),
                    verify=VERIFY_SSL_CERTIFICATE,
                )

                _content = StringIO(_file.content)

                file_info = s.post(
                    GITLAB_URL + '%s/uploads' % GITLAB_PROJECT,
                    headers={
                        'X-CSRF-Token': token,
                    },
                    files={
                        'file': (
                            attachment['filename'],
                            _content
                        )
                    },
                    verify=VERIFY_SSL_CERTIFICATE
                )

                del _content

                # now we got the upload URL. Let's post the comment with an
                # attachment

                requests.post(
                    GITLAB_URL + 'api/v3/projects/%s/issues/%s/notes' % (GITLAB_PROJECT_ID, gl_issue),
                    headers={'PRIVATE-TOKEN': GITLAB_USER_TOKENS.get(author, GITLAB_TOKEN)},
                    verify=VERIFY_SSL_CERTIFICATE,
                    data={
                        'body': '[%s](%s)' % (
                            attachment['filename'],
                            file_info.json()['link']['url']
                        )
                    }
                )

            s.get(GITLAB_URL + 'users/sign_out')
