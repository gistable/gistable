"""
Example snippet on how to sync from JIRA to omnifocus.

The main function is OmniFocus.sync_jira_to_omnifocus().
OmniFocus.process_jira_data() is customized to filter projects based on my own needs and will need updating.
"""
from applescript import AppleScript, ScriptError
from datetime import datetime
from json import JSONDecoder
from logging import getLogger
from urllib2 import urlopen

log = getLogger('omni_jira')

OMNI_FOLDER = "/Users/<user>/Library/Containers/com.omnigroup.OmniFocus2.MacAppStore/Data/Documents"
TASK_FILENAME = "jira_tasks.txt"
JIRA_URL = 'https://mysite.atlassian.net/browse/'
PERSPECTIVE = 'Projects'  # I use a custom perspective which just shows the project with my jira issues


FINISH_SCRIPT = lambda task, status, note, project: """
on run
    set theDate to current date
    set theTask to "{0}"
    set theStatus to "Status: {1}\n"
    set theNote to "{2}"
    set theContextName to "jira"
    set theProjectName to "{3}"

    tell application "OmniFocus"
        tell front document
            set theContext to first flattened context where its name = theContextName
            set theProject to first flattened project where its name = theProjectName
            if exists (first flattened task where its name = theTask and its context = theContext) then
                -- Tasks exists, update the detail if necessary
                set selectedTask to first flattened task where its name = theTask
                set selectedNote to the paragraphs of the note of the selectedTask
                -- Overwrite the note detail if the status has changed
                if (item 1 of the selectedNote is not theStatus) then
                    set the note of the selectedTask to theNote
                end if
                -- Complete task if necessary
                if (not completed of the selectedTask) then
                    set the completed of the selectedTask to true
                end if
            end if
        end tell
    end tell
end run
""".format(task, status, note, project)


GET_SCRIPT = lambda perspective, folder, filename: """
on run
    set thePerspective to "{0}"
    set POSIXpath to POSIX path of "{1}/{2}"
    tell front document of application "OmniFocus"
        tell front document window
            set perspective name to thePerspective
            save in POSIXpath as "public.text"
        end tell
    end tell
end run
""".format(perspective, folder, filename)


UPDATE_SCRIPT = lambda task, status, flag, dueDate, note, project: """
on run
    set theDate to current date
    set theTask to "{0}"
    set theStatus to "Status: {1}\n"
    set theFlag to {2}
    set theDueDate to {3}
    set theNote to "{4}"
    set theContextName to "jira"
    set theProjectName to "{5}"

    tell application "OmniFocus"
        tell front document
            set theContext to first flattened context where its name = theContextName
            set theProject to first flattened project where its name = theProjectName

            if exists (first flattened task where its name = theTask and its context = theContext) then
                -- Tasks exists, update the detail if necessary
                set selectedTask to first flattened task where its name = theTask
                set selectedNote to the paragraphs of the note of the selectedTask
                -- Overwrite the note detail if the status has changed
                if (item 1 of the selectedNote is not theStatus) then
                    set the note of the selectedTask to theNote
                end if
                -- Flag task if necessary (but don't remove existing flags)
                if (not flagged of the selectedTask and theFlag) then
                    set the flagged of the selectedTask to theFlag
                end if
                -- Check due date
                set selectedDueDate to the due date of the selectedTask
                if (theDueDate is not missing value and theDueDate is not selectedDueDate) then
                    set the due date of the selectedTask to theDueDate
                end if
                -- Ensure task not marked as completed
                if (completed of the selectedTask) then
                    set the completed of the selectedTask to false
                end if
            else
                -- Add new Task
                tell theProject to make new task with properties {{name:theTask, note:theNote, context:theContext}}
            end if
        end tell
    end tell
end run
""".format(task, status, 'true' if flag else 'false',
           'date "{0} 5:00 PM"'.format(dueDate.strftime('%m/%d/%Y')) if dueDate else 'missing value', note,
           project)


def stringToDatetime(s):
    """
    Try various things to convert string to datetime.
    :param s:  string to parse
    :return: datetime object
    """
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    except (ValueError, TypeError):
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
    except (ValueError, TypeError):
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    return None


class OmniFocus(object):
    """
    Class for getting issues from JIRA and creating / updating OmniFocus tasks.

    See OmniFocus.sync_jira_to_omnifocus() -- this is the function that calls everything else.

    You'll have to OmniFocus.customize process_jira_data(), as it filters tasks based on my needs.
    """
    def __init__(self):
        self.data = None

    @staticmethod
    def finish_task(task, status, note, project):
        AppleScript(FINISH_SCRIPT(task, status, note, project)).run()

    @staticmethod
    def get_tasks():
        AppleScript(GET_SCRIPT(PERSPECTIVE, OMNI_FOLDER, TASK_FILENAME)).run()

    @staticmethod
    def update_task(task, status, flag, dueDate, note, project):
        AppleScript(UPDATE_SCRIPT(task, status, flag, dueDate, note, project)).run()

    @staticmethod
    def load_jira_data(project_key, username, password):
        """
        Load the data from jira, and build a list that has the details you want in the OmniFocus notes.

        :param project_key: 3-4 letter jira project key (project letters in front of the issue number)
        :param username: jira username
        :param password: jira password
        :return:
        """
        data = []
        url = '{0}rest/api/2/search?jql=project='.format(JIRA_URL) + \
              '{0}&maxResults=1000&os_username={1}&os_password={2}'.format(project_key, username, password)
        f = urlopen(url)
        response = f.read()
        f.close()
        jira_data = JSONDecoder().decode(response)
        for issue in jira_data['issues']:
            key = issue['key']
            url = '{0}{1}'.format(JIRA_URL, key)
            name = issue['fields']['assignee']['name']
            title = issue['fields']['summary'].replace('"', "'")
            status = issue['fields']['status']['name']
            dueDate = stringToDatetime(issue['fields']['duedate'])
            if issue['fields']['description']:
                description = issue['fields']['description'].encode('ascii', 'ignore').replace('"', "'")\
                    .replace("\\'", "'")
            else:
                description = ''
            # Build the task details and store them on the data
            task = '{0}: {1}'.format(key, title)
            note = 'Status: {0}\n{1}\n\n{2}'.format(status, url, description)
            data.append({'key': key, 'task': task, 'name': name, 'status': status, 'dueDate': dueDate, 'note': note})
        return data

    @staticmethod
    def process_jira_data(data):
        """
        Processes the data from jira.  Note - you'll need to customize this.  It current filters to my username,
        and to status items specific to my project.
        :param data:
        :return:
        """
        processed = []
        for item in data:
            if item['name'] == 'amorris' and item['status'] in ('Open', 'Reopened', 'In Progress', 'In Progress - Warn',
                                                                'In Progress - Alert'):
                if item['status'] in ('In Progress', 'In Progress - Warn', 'In Progress - Alert'):
                    flag = True
                else:
                    flag = False
                processed.append({'task': item['task'], 'status': item['status'], 'done': False,
                                  'flag': flag, 'dueDate': item['dueDate'], 'note': item['note']})
            elif item['name'] == 'amorris' and item['status'] in ('Closed', 'Resolved'):
                processed.append({'task': item['task'], 'status': item['status'], 'done': True, 'flag': False,
                                  'dueDate': None, 'note': item['note']})
        return processed

    def sync_jira_to_omnifocus(self, project, project_key, username, password):
        """
        Main function to call.  This calls all the other functions to get information from jira into OmniFocus.
        :param project:  The full name of the project
        :param project_key:  3-4 letter jira project key (project letters in front of the issue number)
        :param username:  jira username
        :param password:  jira password
        :return:
        """
        log.info('Loading Jira Issues')
        data = self.load_jira_data(project_key, username, password)
        processed = self.process_jira_data(data)
        log.info('Updating OmniFocus')
        for item in processed:
            if not item['done']:
                log.info('Update {0}'.format(item['task']))
                try:
                    # This adds / updates a task in OmniFocus
                    self.update_task(item['task'], item['status'], item['flag'], item['dueDate'], item['note'], project)
                except ScriptError, e:
                    log.warn('Task Failed: {0}: {1}'.format(item['task'], e))
                    msg = UPDATE_SCRIPT(item['task'], item['status'], item['flag'], item['dueDate'], item['note'],
                                        project)
                    log.debug(msg)
            else:
                try:
                    # This auto-finishes a task in jira
                    self.finish_task(item['task'], item['status'], item['note'], project)
                except ScriptError, e:
                    log.warn('Finished Task Ignored: {0}: {1}'.format(item['task'], e))
                    msg = FINISH_SCRIPT(item['task'], item['status'], item['note'], project)
                    log.debug(msg)